import bpy
from bpy.types import Operator
from bpy.app.handlers import persistent
import gpu
from gpu_extras.batch import batch_for_shader
from gpu.types import GPUShader
from mathutils import Color

from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

class MGTOOLSOverlayManager():
    draw_handle = None
    shader = None
    initialized = False

    # Shader ##########################################################

    vertex_shader_simple = '''
            in vec3 position;
            in vec4 color;
            uniform mat4 perspective_matrix;
            uniform mat4 object_matrix;
            uniform float point_size;
            uniform float cutoff_radius;
            uniform float global_alpha;
            out vec4 f_color;
            out float f_cutoff_radius;
            void main()
            {
                gl_Position = perspective_matrix * object_matrix * vec4(position, 1.0f);
                gl_PointSize = point_size;
                f_color = vec4(color[0], color[1], color[2], global_alpha);
                f_cutoff_radius = cutoff_radius;
            }
        '''
    fragment_shader_simple = '''
            in vec4 f_color;
            in float f_cutoff_radius;
            out vec4 fragColor;
            void main()
            {
                vec2 cxy = 2.0f * gl_PointCoord - 1.0f;
                float r = dot(cxy, cxy);
                if(r > f_cutoff_radius){
                    discard;
                }
                fragColor = f_color;
            }
        '''


    # Basics ##########################################################

    @classmethod
    def init(self):
        print("Init MGTOOLSOverlayManager")

        if(self.initialized):
            return

        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, (), "WINDOW", "POST_VIEW")
        bpy.app.handlers.load_pre.append(watcher)
        self.initialized = True

    @classmethod
    def deinit(self):
        if None != self.draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, 'WINDOW')
        self.draw_handle = None
        if True == watcher in bpy.app.handlers.load_pre:
            bpy.app.handlers.load_pre.remove(watcher)
        self.initialized = False


    # Drawing ##########################################################

    @classmethod
    def create_batch(self, meshobj_org):
        # checks ---------------------------
        if None == meshobj_org or 'MESH' != meshobj_org.type :
            print("No valid mesh object")
            return
        
        # get the active vertex group - otherwise exit
        activeVG = meshobj_org.vertex_groups.active

        if None == activeVG:
            print("No active vertex group")
            return

        # prepare mesh ---------------------------
        # https://docs.blender.org/api/blender2.8/bpy.types.Depsgraph.html
        # evaluate dependency graph of selected object
        depsgraph = bpy.context.evaluated_depsgraph_get()
        # get object with dependency graph applied
        meshobj_eval = meshobj_org.evaluated_get(depsgraph)

        # get vertex positions ---------------------------
        vertices = meshobj_eval.data.vertices
        vertPositions = []
        for v in vertices:
            vertPositions.append(v.co)

        if (0 >= len(vertPositions)):
            print("No vert positions")
            return

        # get weight colors ---------------------------
        vertWeights = MGTOOLS_functions_helper.get_weights(meshobj_eval.data, activeVG)
        vertWeightColors = []
        for w in vertWeights:
            vertWeightColors.append(MGTOOLS_functions_helper.convertWeight2Color(w))

        # sanity checks ---------------------------
        if(len(vertWeightColors) != len(vertPositions)):
            print("positions {}, weights {} and colors {} count differs".format(len(vertPositions), len(vertWeights), len(vertWeightColors)))
            return

        # prepare shader and draw ---------------------------
        self.shader = GPUShader(self.vertex_shader_simple, self.fragment_shader_simple)

        if(None == self.shader):
            print("Shader is not valid")
            return

        self.batch = batch_for_shader(self.shader, 'POINTS', {"position": vertPositions, "color": vertWeightColors,})

    @classmethod
    def draw_callback(self):
        if False == self.initialized:
            return
        
        # print("Drawing...> num selected objects: {}".format(len(bpy.context.selected_objects)))

        if 0 >= len(bpy.context.selected_objects):
            return

        # ----------------------------------
        # tmp: find first MESH-object - otherwise exit
        drawmesh = MGTOOLS_functions_macros.get_first_selected_mesh()
        if None == drawmesh:
            return

        # prepare mesh for drawing ----------------------------------
        # Note: we need this to take changes from modifiers or armature deformation into account

        # drawmesh = obj.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        # evaluate dependency graph of selected object
        # depsgraph = bpy.context.evaluated_depsgraph_get()
        # get object with dependency graph applied
        # object_eval = obj.evaluated_get(depsgraph)
        # get mesh
        # drawmesh = object_eval.data

        # ----------------------------------
        # update the batch to show changed vertex weights and positions! 
        self.create_batch(drawmesh)

        if(None == self.shader):
            return

        self.shader.bind()

        # update shader parameters
        mgtools_props_obj = bpy.context.object.mgtools
        pm = bpy.context.region_data.perspective_matrix
        self.shader.uniform_float("perspective_matrix", pm)
        self.shader.uniform_float("object_matrix", drawmesh.matrix_world)
        self.shader.uniform_float("point_size", mgtools_props_obj.p_weightdisplay_point_size)
        self.shader.uniform_float("cutoff_radius", mgtools_props_obj.p_weightdisplay_point_radius)
        self.shader.uniform_float("global_alpha", mgtools_props_obj.p_weightdisplay_global_alpha)

        # draw
        self.batch.draw(self.shader)


        # cleanup ----------------------------------
        # obj.to_mesh_clear()



# ///////////////////////////////////////////////////////////////////////////////////////////////////

@persistent
def watcher(scene):
    MGTOOLSOverlayManager.deinit()