import traceback
import gpu
from gpu.types import GPUShader
from gpu_extras.batch import batch_for_shader
from mathutils import Color
import bpy
from bpy.types import Operator
from bpy.app.handlers import persistent

from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros


def overlay_update(scene, depsgraph):
    MGTOOLSOverlayManager.dirty = True


class MGTOOLSOverlayManager():
    draw_handle = None
    shader = None
    batch = None
    color_batch = None
    initialized = False
    dirty = True

    # Shader ##########################################################

    vertex_shader_inputs = '''
            in vec3 position;
            in vec4 color;
            uniform mat4 perspective_matrix;
            uniform mat4 object_matrix;
            uniform float point_size;
            uniform float cutoff_radius;
            uniform float global_alpha;
            out vec4 f_color;
            out float f_cutoff_radius;
        '''
    vertex_shader_body = '''
            void main()
            {
                gl_Position = perspective_matrix * object_matrix * vec4(position, 1.0f);
                gl_PointSize = point_size;
                f_color = vec4(color[0], color[1], color[2], global_alpha);
                f_cutoff_radius = cutoff_radius;
            }
        '''
    fragment_shader_inputs = '''
            in vec4 f_color;
            in float f_cutoff_radius;
            out vec4 fragColor;
        '''
    fragment_shader_body = '''
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

    # Legacy Blender versions require the declarations in the GLSL source.
    vertex_shader_simple = vertex_shader_inputs + vertex_shader_body
    fragment_shader_simple = fragment_shader_inputs + fragment_shader_body


    # Basics ##########################################################

    @classmethod
    def init(self):
        print("Init MGTOOLSOverlayManager")

        if(self.initialized):
            return

        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, (), "WINDOW", "POST_VIEW")
        bpy.app.handlers.load_pre.append(watcher)
        if overlay_update not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(overlay_update)
        self.dirty = True
        self.initialized = True

    @classmethod
    def deinit(self):
        if None != self.draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, 'WINDOW')
        self.draw_handle = None
        self.shader = None
        self.batch = None
        self.color_batch = None
        self.dirty = True
        if True == watcher in bpy.app.handlers.load_pre:
            bpy.app.handlers.load_pre.remove(watcher)
        if overlay_update in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(overlay_update)
        self.initialized = False


    # Drawing ##########################################################

    @classmethod
    def create_shader(self):
        # GPUShaderCreateInfo replaced the GPUShader GLSL-source constructor in Blender 4.0+.
        shader_create_info_type = getattr(gpu.types, "GPUShaderCreateInfo", None)
        stage_interface_type = getattr(gpu.types, "GPUStageInterfaceInfo", None)
        create_from_info = getattr(gpu.shader, "create_from_info", None)

        if None != shader_create_info_type and None != stage_interface_type and None != create_from_info:
            interface = stage_interface_type("mgtools_overlay_interface")
            interface.flat("VEC4", "f_color")
            interface.flat("FLOAT", "f_cutoff_radius")

            shader_info = shader_create_info_type()
            shader_info.vertex_in(0, "VEC3", "position")
            shader_info.vertex_in(1, "VEC4", "color")
            shader_info.vertex_out(interface)
            shader_info.push_constant("MAT4", "perspective_matrix")
            shader_info.push_constant("MAT4", "object_matrix")
            shader_info.push_constant("FLOAT", "point_size")
            shader_info.push_constant("FLOAT", "cutoff_radius")
            shader_info.push_constant("FLOAT", "global_alpha")
            shader_info.fragment_out(0, "VEC4", "fragColor")
            shader_info.vertex_source(self.vertex_shader_body)
            shader_info.fragment_source(self.fragment_shader_body)

            shader = create_from_info(shader_info)
            del interface
            del shader_info
            return shader

        # Blender versions before GPUShaderCreateInfo use this fallback.
        return GPUShader(self.vertex_shader_simple, self.fragment_shader_simple)

    @classmethod
    def create_batch(self, meshobj_org, overlay_type, meshobj_eval=None):
        if overlay_type == 'WEIGHT':
            self.batch = None
        else:
            self.color_batch = None

        # checks ---------------------------
        if None == meshobj_org or 'MESH' != meshobj_org.type :
            print("No valid mesh object")
            return
        
        # prepare mesh ---------------------------
        # https://docs.blender.org/api/blender2.8/bpy.types.Depsgraph.html
        # evaluate dependency graph of selected object
        if meshobj_eval is None:
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

        if overlay_type == 'WEIGHT':
            activeVG = meshobj_org.vertex_groups.active
            if activeVG is None:
                return
            vertWeights = MGTOOLS_functions_helper.get_weights(meshobj_eval.data, activeVG)
            vertColors = [MGTOOLS_functions_helper.convert_weight_2_color(w) for w in vertWeights]
        else:
            color_attributes = getattr(meshobj_eval.data, 'color_attributes', None)
            attribute = getattr(color_attributes, 'active_color', None) if color_attributes is not None else None
            if attribute is None or attribute.domain not in {'POINT', 'CORNER'}:
                return
            vertColors = MGTOOLS_functions_helper.get_color_attribute_colors(meshobj_eval.data, attribute)
            for vertex_index, color in enumerate(vertColors):
                if bpy.context.scene.mgtools.p_vertexcolordisplay_alpha:
                    color = (color[3], color[3], color[3], 1.0)
                vertColors[vertex_index] = color

        # sanity checks ---------------------------
        if(len(vertColors) != len(vertPositions)):
            print("positions {} and colors {} count differs".format(len(vertPositions), len(vertColors)))
            return

        # prepare shader and draw ---------------------------
        if None == self.shader:
            self.shader = self.create_shader()

        if(None == self.shader):
            print("Shader is not valid")
            return

        new_batch = batch_for_shader(self.shader, 'POINTS', {"position": vertPositions, "color": vertColors,})
        if overlay_type == 'WEIGHT':
            self.batch = new_batch
        else:
            self.color_batch = new_batch

    @classmethod
    def draw_batch(self, meshobj, batch, point_size, point_radius, global_alpha):
        if batch is None:
            return
        self.shader.uniform_float("object_matrix", meshobj.matrix_world)
        self.shader.uniform_float("point_size", point_size)
        self.shader.uniform_float("cutoff_radius", point_radius)
        self.shader.uniform_float("global_alpha", global_alpha)
        batch.draw(self.shader)

    @classmethod
    def draw_callback(self):
        if False == self.initialized:
            return
        
        # print("Drawing...> num selected objects: {}".format(len(bpy.context.selected_objects)))

        if 0 >= len(bpy.context.selected_objects):
            return

        # ----------------------------------
        # Use the active mesh when possible so the displayed settings and data
        # always belong to the same object.
        drawmesh = bpy.context.view_layer.objects.active
        if drawmesh is None or drawmesh.type != 'MESH':
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
        mgtools_props_scene = bpy.context.scene.mgtools
        if not mgtools_props_scene.p_weightdisplay_isenabled and not mgtools_props_scene.p_vertexcolordisplay_isenabled:
            return

        region_data = bpy.context.region_data
        if region_data is None:
            return

        if self.dirty:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            drawmesh_eval = drawmesh.evaluated_get(depsgraph)
            if mgtools_props_scene.p_weightdisplay_isenabled:
                try:
                    self.create_batch(drawmesh, 'WEIGHT', drawmesh_eval)
                except Exception:
                    self.batch = None
                    traceback.print_exc()
            if mgtools_props_scene.p_vertexcolordisplay_isenabled:
                try:
                    self.create_batch(drawmesh, 'COLOR', drawmesh_eval)
                except Exception:
                    self.color_batch = None
                    traceback.print_exc()
            self.dirty = False

        if self.shader is None:
            return

        self.shader.bind()

        # update shader parameters
        pm = region_data.perspective_matrix
        self.shader.uniform_float("perspective_matrix", pm)
        if mgtools_props_scene.p_weightdisplay_isenabled:
            self.draw_batch(drawmesh, self.batch, mgtools_props_scene.p_weightdisplay_point_size, mgtools_props_scene.p_weightdisplay_point_radius, mgtools_props_scene.p_weightdisplay_global_alpha)
        if mgtools_props_scene.p_vertexcolordisplay_isenabled:
            self.draw_batch(drawmesh, self.color_batch, mgtools_props_scene.p_weightdisplay_point_size, mgtools_props_scene.p_weightdisplay_point_radius, mgtools_props_scene.p_weightdisplay_global_alpha)


        # cleanup ----------------------------------
        # obj.to_mesh_clear()



# ///////////////////////////////////////////////////////////////////////////////////////////////////

@persistent
def watcher(scene):
    MGTOOLSOverlayManager.deinit()