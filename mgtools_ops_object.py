import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

# we use this for simple debug tests
class MGTOOLS_OT_object_snapshot(Operator):
    bl_idname = "mgtools.object_snapshot"
    bl_label = "Snapshot tool"
    bl_description = "Make a snapshot of objects"

    def execute(self, context):
        print ("MGTOOLS_OT_object_snapshot")

        mgtools_props_obj = bpy.context.object.mgtools

        # properties
        frame_start = mgtools_props_obj.p_snapshot_frame_start
        frame_end = mgtools_props_obj.p_snapshot_frame_end
        merge_objects = mgtools_props_obj.p_snapshot_merge_objects
        prefix = ""
        if True == mgtools_props_obj.p_snapshot_use_name_prefix:
            prefix = mgtools_props_obj.p_snapshot_name_prefix


        if frame_end < frame_start:
            print ("Invalid frame range from({}) to({})".format(frame_start, frame_end))
            return{'CANCELLED'}

        source_objects = bpy.context.selected_objects

        # set animation frame to the start position
        for i in range(frame_start, frame_end):
            # print ("Snapshotting frame: {}".format(i))
            
            # set frame
            bpy.context.scene.frame_set(i)

            # make snapshot
            MGTOOLS_functions_macros.make_snapshot_from(source_objects, merge_objects, prefix, True)

        
        # print("Test properties: {}".format(bpy.types.Scene.mgtools.p_weightdisplay_point_size))
        return{'FINISHED'}

class MGTOOLS_OT_object_pivot_copy(Operator):
    bl_idname = "mgtools.object_pivot_copy"
    bl_label = "Pivot copy tool"
    bl_description = "Copy pivot from the last selected objects to the rest of the selection"

    def execute(self, context):
        print ("MGTOOLS_OT_object_pivot_copy")
        
        selected_objects_count = len(bpy.context.selected_objects)

        if 2 > selected_objects_count:
            return

        ref_object = bpy.context.view_layer.objects.active
        target_objects = bpy.context.selected_objects.copy()
        target_objects.remove(ref_object)

        print("selected_objects: {}".format(bpy.context.selected_objects))
        print("ref_object: {}".format(ref_object))
        print("target_objects: {}".format(target_objects))

        MGTOOLS_functions_macros.set_pivot(target_objects, ref_object.location, ref_object.rotation_euler, False)

        return{'FINISHED'}

class MGTOOLS_OT_object_parent_set(Operator):
    bl_idname = "mgtools.object_parent_set"
    bl_label = "Set Parent to Active"
    bl_description = "Set parent of all selected objects to active object"

    def execute(self, context):
        parent = bpy.context.view_layer.objects.active
        for child in bpy.context.selected_objects:
            if child == parent: continue
            MGTOOLS_functions_helper.set_parent(child, parent, True)
        return{'FINISHED'}

class MGTOOLS_OT_object_parent_clear(Operator):
    bl_idname = "mgtools.object_parent_clear"
    bl_label = "Clear Parent"
    bl_description = "Clear parent of all selected objects"

    def execute(self, context):
        for child in bpy.context.selected_objects:
            MGTOOLS_functions_helper.set_parent(child, None, True)
        return{'FINISHED'}