import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros


class MGTOOLS_OT_auto_update_motion_paths(Operator):
    bl_idname = "mgtools.animation_auto_update_motion_paths"
    bl_label = ""
    bl_description = ""

    update_timer = None
    time_duration_cached : bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        return not mgtools_props_scene.p_motionpaths_is_auto_update_active

    def modal(self, context, event):
        # check if auto-update button is still active
        mgtools_props_scene = bpy.context.scene.mgtools
        if False == mgtools_props_scene.p_motionpaths_is_auto_update_active:
            self.cancel(context)
            return {'CANCELLED'}

        # do action
        if event.type == 'TIMER':
            if self.time_duration_cached != self.update_timer.time_duration:
                self.time_duration_cached = self.update_timer.time_duration
                print ("update modal")
                MGTOOLS_functions_macros.motion_path_update()

        return {'PASS_THROUGH'}

    def execute(self, context):
        print ("execute auto motion paths update")
        # set the flag
        mgtools_props_scene = bpy.context.scene.mgtools
        mgtools_props_scene.p_motionpaths_is_auto_update_active = True

        wm = context.window_manager

        # setup timer event
        freq = 2
        self.update_timer = wm.event_timer_add(freq, window=context.window)

        # setup modal handler
        wm.modal_handler_add(self)


        return {'RUNNING_MODAL'}

    def cancel(self, context):
        print ("cancel auto motion paths update")
        wm = context.window_manager
        # clear timer event
        wm.event_timer_remove(self.update_timer)

        # clear flag
        mgtools_props_scene = bpy.context.scene.mgtools
        mgtools_props_scene.p_motionpaths_is_auto_update_active = False


class MGTOOLS_OT_copy_animation_data(Operator):
    bl_idname = "mgtools.animation_copy_animation_data"
    bl_label = "Copy Animation Data"
    bl_description = "Copies animation data from one object to another. Will override any existing animation data"

    def execute(self, context):
        
        mgtools_props_scene = bpy.context.scene.mgtools

        obj_from = mgtools_props_scene.p_animation_copy_data_source
        obj_to = mgtools_props_scene.p_animation_copy_data_target

        print ("copy_animation_data(from: {}, to: {})".format(obj_from, obj_to))

        if obj_from != obj_to:
            MGTOOLS_functions_helper.copy_animation_data(obj_from, obj_to)

        return{'FINISHED'}