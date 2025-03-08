# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

class MGTOOLS_OT_particle_hair_to_mesh(Operator):
    bl_idname = "mgtools.particle_hair_to_mesh"
    bl_label = "Particle Hair 2 Mesh"
    bl_description = "Convert particle hair to meshes"

    def execute(self, context):
        print ("MGTOOLS_OT_particle_hair_to_mesh")
        
        # read properties -----------------------------------
        mgtools_props_scene = bpy.context.scene.mgtools

        hair_to_mesh_thickness = mgtools_props_scene.p_particle_hair_to_mesh_thickness
        hair_to_mesh_resolution = int(max(0, mgtools_props_scene.p_particle_hair_to_mesh_resolution))
        hair_to_mesh_name = mgtools_props_scene.p_particle_hair_to_mesh_name

        # vars -----------------------------------
        selected_objects_count = len(bpy.context.selected_objects)

        # active_object = bpy.context.view_layer.objects.active
        to_process = bpy.context.selected_objects.copy()

        # print("active_object: {}".format(active_object))
        print(f"selected_objects: {to_process}")

        # per object...
        for obj in to_process:
            created_objs = []

            # find relevant modifier and get converted meshes
            for mod in obj.modifiers:
                if 'PARTICLE_SYSTEM' == mod.type and mod.show_viewport == True:
                    
                    # re-select object
                    MGTOOLS_functions_macros.select_only(obj)

                    #convert to mesh
                    print(f"convert modifier: {mod}")
                    bpy.ops.object.modifier_convert(modifier=mod.name)

                    created_objs.append(bpy.context.view_layer.objects.active)

                    # converted hair is now selected - convert to curve
                    print(f"convert to curves: {mod}")
                    bpy.ops.object.convert(target='CURVE')

            print("Created Objects:")
            print(created_objs)

            # setup created curves
            for mesh in created_objs:
                mesh.data.bevel_mode = 'ROUND'
                mesh.data.bevel_depth = hair_to_mesh_thickness
                mesh.data.bevel_resolution = hair_to_mesh_resolution
                mesh.data.use_fill_caps = True
                mesh.name = hair_to_mesh_name

            # convert curves to meshes
            MGTOOLS_functions_macros.select_objects(created_objs)
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.shade_smooth()

        return{'FINISHED'}

class MGTOOLS_OT_modifier_toggle(Operator):
    bl_idname = "mgtools.modifier_toggle"
    bl_label = "Modifier Toggle"
    bl_description = "Toggles show-in-viewport state of all modifiers with the given name on all selected objects"

    modifier_toggle_name: bpy.props.StringProperty(
        name = 'Modifier',
        default = ''
        )

    def execute(self, context):
        print ("MGTOOLS_OT_modifier_toggle")
        
        # read properties -----------------------------------
        # mgtools_props_scene = bpy.context.scene.mgtools

        # modifier_toggle_name = mgtools_props_scene.p_modifier_toggle_name

        # vars -----------------------------------
        selected_objects_count = len(bpy.context.selected_objects)

        # active_object = bpy.context.view_layer.objects.active
        to_process = bpy.context.selected_objects.copy()

        # print("active_object: {}".format(active_object))
        print(f"selected_objects: {to_process}")

        toggle_state = -1

        # per object...
        for obj in to_process:
            # find relevant modifier and get converted meshes
            for mod in obj.modifiers:
                if self.modifier_toggle_name == mod.name:
                    if 0 > toggle_state:
                        toggle_state = not mod.show_viewport
                    mod.show_viewport = toggle_state

        return{'FINISHED'}

class MGTOOLS_OT_vertices_to_attribute(Operator):
    bl_idname = "mgtools.vertices_to_attribute"
    bl_label = "Vertices to Attribute"
    bl_description = "Copies vertex positions to a custom attribute"

    attribute_name: bpy.props.StringProperty(
        name = 'positions',
        default = ''
        )
    relative: bpy.props.BoolProperty(
        name = 'relative',
        default = True
        )

    def execute(self, context):
        print ("MGTOOLS_OT_vertices_to_attribute")

        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        # base data -------
        meshdata = meshobj.data
        # as attributes == base mesh vertices we can and should define this here
        array_size = len(meshdata.vertices)*3

        vertex_positions = [0]*array_size
        # prepare snapshot data (array is serialized: v1.x, v1.y, v1.z, v2.x, v2.y, v2.z, etc. )
        meshdata.vertices.foreach_get('co', vertex_positions)

        # create a clone to read evaluated data from
        out_list = MGTOOLS_functions_macros.make_snapshot_from(
                source_objects_raw=[meshobj],
                merge=False, 
                prefix="", 
                postfix="_snapshot", 
                select_clones=False, 
                type_filter=None)
        meshobj_snapshot = out_list[0]
        meshobj_snapshot.modifiers.clear()
        meshdata_evaluated = MGTOOLS_functions_helper.get_evaluated_meshdata(meshobj_snapshot)
        bpy.data.objects.remove(meshobj_snapshot)

        vertex_positions_evaluated = [0]*array_size
        meshdata_evaluated.vertices.foreach_get('co', vertex_positions_evaluated)

        # prepare the data to be written
        vertex_positions_final = vertex_positions_evaluated

        # if 'relative' then we are only interested on the deltas from the base position
        if self.relative:
            vertex_positions_delta = [x-y for x, y in zip(vertex_positions_evaluated, vertex_positions)]
            vertex_positions_final = vertex_positions_delta

        # set to custom attribute
        attribute = meshdata.attributes.new(name=self.attribute_name, type="FLOAT_VECTOR", domain="POINT")
        attribute.data.foreach_set("vector", vertex_positions_final)

        return{'FINISHED'}