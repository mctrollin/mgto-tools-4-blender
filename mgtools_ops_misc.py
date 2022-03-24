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
        hair_to_mesh_resolution = mgtools_props_scene.p_particle_hair_to_mesh_resolution
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