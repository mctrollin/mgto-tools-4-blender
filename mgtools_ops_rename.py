import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_functions_rename import MGTOOLS_functions_rename

class MGTOOLS_OT_rename_bones(Operator):
    bl_idname = "mgtools.rename_bones"
    bl_label = "Rename bones and vertex groups"
    bl_description = "Rename bones of an armature"

    def execute(self, context):
        print ("MGTOOLS_OT_rename_bones")

        mgtools_props_scene = bpy.context.scene.mgtools

        # properties
        bone_names_mapping_file_path = mgtools_props_scene.p_rename_mapping_file_path
        invert_mapping = mgtools_props_scene.p_rename_mapping_inverse
        
        # get armature
        armature_object = MGTOOLS_functions_macros.get_first_selected_armature()

        if None == armature_object:
            armature_object = MGTOOLS_functions_macros.get_armature_from_first_selected_mesh()

        if None != armature_object:
            # rename bones
            MGTOOLS_functions_rename.rename_bones(armature_object, bone_names_mapping_file_path, invert_mapping)
        else:
            print("No armature")
       
        return{'FINISHED'}

class MGTOOLS_OT_rename_vertexgroups(Operator):
    bl_idname = "mgtools.rename_vertexgroups"
    bl_label = "Rename vertex groups"
    bl_description = "Rename vertex groups of a mesh"

    def execute(self, context):
        print ("MGTOOLS_OT_rename_vertexgroups")

        mgtools_props_scene = bpy.context.scene.mgtools

        # properties
        bone_names_mapping_file_path = mgtools_props_scene.p_rename_mapping_file_path
        invert_mapping = mgtools_props_scene.p_rename_mapping_inverse
        
        # get mesh
        mesh_object = MGTOOLS_functions_macros.get_first_selected_mesh()
       
        if None != mesh_object:
            # rename vertex groups
            MGTOOLS_functions_rename.rename_vertexgroups(mesh_object, bone_names_mapping_file_path, invert_mapping)
        else:
            print("No mesh")
       
        return{'FINISHED'}

class MGTOOLS_OT_rename_print_bones(Operator):
    bl_idname = "mgtools.rename_print_bones"
    bl_label = "Print bone names"
    bl_description = "Outputs bone names as string in the console and to the clipboard"

    def execute(self, context):
        print ("MGTOOLS_OT_rename_print_bones")

        # get armature
        armature_object = MGTOOLS_functions_macros.get_first_selected_armature()
       
        if None != armature_object:
            out_string = ""
            for bone in armature_object.data.bones:
                out_string += bone.name + "\n"
            print(out_string)

            # copy to clipboard
            bpy.context.window_manager.clipboard = out_string

        return{'FINISHED'}

class MGTOOLS_OT_rename_mesh_from_object(Operator):
    bl_idname = "mgtools.rename_mesh_from_object"
    bl_label = "Set Mesh name from Object name"
    bl_description = "For all selected Mesh Objects will copies the name of the mesh object to the mesh data object so both have the same name."

    def execute(self, context):
        print ("MGTOOLS_OT_rename_print_bones")

        target_objects = bpy.context.selected_objects.copy()
       
        if None != target_objects:
            out_string = ""
            for target_object in target_objects:
                if 'MESH' == target_object.type:
                    target_object.data.name = target_object.name
       
        return{'FINISHED'}
