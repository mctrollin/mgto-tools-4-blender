import copy
import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

# create new armature using selected bones as reference and respecting the original hierarchy
class MGTOOLS_OT_extract_clone_bones(Operator):
    bl_idname = "mgtools.rigging_extract_clone_bones"
    bl_label = ""
    bl_description = ""

    def execute(self, context):

        # if 'EDIT' != bpy.ops.object.mode_set

        # get sources ---------------------------
        if 0 >= len(bpy.context.selected_objects):
            print ("Nothing selected")
            return {'CANCELLED'}

        # get source armature
        source_armature = MGTOOLS_functions_macros.get_first_selected_armature()

        if None == source_armature:
            print ("Can't find source armature")
            return {'CANCELLED'}

        if None == context.selected_bones:
            print ("No selected bones")
            return {'CANCELLED'}

        # get source bone names (as the references will change if we use the clone method)
        source_ebones = [eb.name for eb in context.selected_bones]

        if 0 >= len(source_ebones):
            print ("No source bones selected")
            return {'CANCELLED'}

      

        # create target armature ---------------------------
        target_armature_data = bpy.data.armatures.new('Target_Armature_Data')
        target_armature = bpy.data.objects.new("Target_Armature", target_armature_data)
        bpy.context.collection.objects.link(target_armature)

        if None == target_armature or None == target_armature_data:
            print ("Can't create armature")
            return {'CANCELLED'}

        # set target armature active
        context.view_layer.objects.active = target_armature

        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools
        use_constraints = mgtools_props_scene.p_rigging_add_rotation_constraints_to_cloned_bones
        new_bones_prefix = mgtools_props_scene.p_rigging_bone_name_prefix

        # create root bones ---------------------------
        root_ebone_name = None
        if True == mgtools_props_scene.p_rigging_add_root_bone:
            # switch to edit mode to be able to add edit-bones
            bpy.ops.object.mode_set(mode='EDIT')
            #create root bone
            root_ebone = self.create_root_ebone(target_armature.data)
            root_ebone.name = new_bones_prefix + root_ebone.name
            root_ebone_name = root_ebone.name


        # create target bones ---------------------------
        for seb in source_ebones:
            # print ("Working on source_ebone: {} -------------------------------------".format(seb))
            # for seb2 in source_ebones:
            #     print ("selected source bones (source_ebone): {}".format(seb2))
            self.clone_ebone(target_armature, source_armature, seb, use_constraints, root_ebone_name, new_bones_prefix)


        return{'FINISHED'}


    def clone_ebone(self, target_armature, source_armature, source_ebone_name, use_constraints, root_ebone_name, new_bones_prefix):

        target_armature_data = target_armature.data

        if None == target_armature_data:
            print ("No armature")
            return

        # switch to edit mode to be able to get edit-bones
        bpy.ops.object.mode_set(mode='EDIT')

        # get source edit-bone ----------------------------
        source_ebone = None
        if source_ebone_name in source_armature.data.edit_bones:
            source_ebone = source_armature.data.edit_bones[source_ebone_name]

        if None == source_ebone:
            print ("Source armature '{}' does not own this edit bone '{}'".format(source_armature.data.name, source_ebone_name))
            return

        # print ("clone_bone({} / {})".format(source_ebone, source_ebone_name))

        target_bone_name_prefix = new_bones_prefix

        # create target edit-bone ----------------------------
        target_ebone = self.clone_ebone_basics(target_armature_data, source_ebone)
        target_ebone.name =  target_bone_name_prefix + target_ebone.name
        if None == target_ebone:
            print ("Error: Can't create this bone bone: {} @ {}".format(source_ebone, target_armature))
            self.report({'ERROR'}, "Error: Can't create this bone bone: {} @ {}".format(source_ebone, target_armature))
            return
        print ("Created target bone (target_ebone): {} from: {} @ {}".format(target_ebone, source_ebone, target_armature))


        # try to find and set correct parent ----------------------------
        source_parent = self.get_deform_parent(source_ebone)
        temp_parent = source_parent
        if None != temp_parent:
            while None != temp_parent:
                temp_target_parent_name = target_bone_name_prefix + temp_parent.name
                if temp_target_parent_name in target_armature_data.edit_bones:
                    target_parent = target_armature_data.edit_bones[temp_target_parent_name]
                    target_ebone.parent = target_parent
                    temp_parent = None
                else:
                    print (" - This (sub)parent is not part of the target_armature data: {}. Continuing searching along hierarchy...".format(temp_parent.name))
                    temp_parent = self.get_deform_parent(temp_parent)
            if None == target_ebone.parent:
                print (" - Source bone: {} has no deform parent in the hierarchy".format(source_ebone))
        else:
            print (" - Source bone: {} has no deform parent".format(source_ebone))

        # assign root bone
        # we have to get it everytime or the assignment may fail bc of the way the script changes modes
        if None == target_ebone.parent and None != root_ebone_name:
            root_ebone = target_armature_data.edit_bones[root_ebone_name]
            print (" - Assigning: {} to root bone: {}".format(target_ebone, root_ebone))
            target_ebone.parent = root_ebone
        

        # switch to object mode to access (pose) bone objects ----------------------------
        # cache bone vars before switching to object mode or they'll be invalid
        target_ebone_name = target_ebone.name
        bpy.ops.object.mode_set(mode='OBJECT')

        # get target pose-bone by edit-bone name
        # print ("Trying to get pose bone by name '{}'".format(target_ebone_name))
        if False == (target_ebone_name in target_armature.pose.bones):
            print (" - Error: Can't find this pose bone: {} @ {}".format(target_ebone_name, target_armature))
            self.report({'ERROR'}, "Error: Can't find this pose bone: {} @ {}".format(target_ebone_name, target_armature))
            return
        target_pbone = target_armature.pose.bones[target_ebone_name]


        # copy info from source bone to target bone ----------------------------
        if True == use_constraints:
            bconstr = target_pbone.constraints.new('COPY_ROTATION')
            bconstr.target = source_armature
            bconstr.subtarget = source_ebone_name


    def clone_ebone_basics(self, target_armature_data, source_ebone):
        ebone = target_armature_data.edit_bones.new(source_ebone.name)
        ebone.head = source_ebone.head
        ebone.tail = source_ebone.tail
        ebone.roll = source_ebone.roll
        ebone.use_connect = source_ebone.use_connect
        return ebone

    def create_root_ebone(self, target_armature_data):
        root_ebone = target_armature_data.edit_bones.new("root")
        root_ebone.head = (0,0,0)
        root_ebone.tail = (0,0,1)
        root_ebone.roll = 0
        root_ebone.use_connect = False
        return root_ebone

    def get_deform_parent(self, ebone):
        for p in ebone.parent_recursive:
            if True == p.use_deform:
                return p
        return None




