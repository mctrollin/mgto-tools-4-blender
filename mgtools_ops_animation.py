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


class MGTOOLS_OT_copy_markers_to_clipboard(Operator):
    bl_idname = "mgtools.animation_copy_markers_to_clipboard"
    bl_label = "Copy Markers"
    bl_description = "Copy timeline markers to the clipboard in a reusable text format"

    def execute(self, context):
        scene = context.scene
        markers = list(scene.timeline_markers)
        markers.sort(key=lambda m: m.frame)

        lines = ["MGTOOLS_MARKERS_V1"]
        for m in markers:
            name = m.name.replace("\t", " ").replace("\n", " ")
            lines.append(f"{name}\t{m.frame}")

        context.window_manager.clipboard = "\n".join(lines)
        return {'FINISHED'}


class MGTOOLS_OT_paste_markers_from_clipboard(Operator):
    bl_idname = "mgtools.animation_paste_markers_from_clipboard"
    bl_label = "Paste Markers"
    bl_description = "Paste timeline markers from the clipboard (expects data copied with the matching format)"

    def execute(self, context):
        scene = context.scene
        mgtools_props_scene = scene.mgtools

        clipboard = context.window_manager.clipboard or ""
        if not clipboard.startswith("MGTOOLS_MARKERS_V1"):
            self.report({'ERROR'}, "Clipboard does not contain valid marker data")
            return {'CANCELLED'}

        lines = [l for l in clipboard.splitlines() if l.strip()]
        if len(lines) <= 1:
            self.report({'WARNING'}, "No markers found in clipboard")
            return {'CANCELLED'}

        merge_mode = mgtools_props_scene.p_animation_marker_clipboard_merge_mode
        if merge_mode == 'REPLACE':
            for m in list(scene.timeline_markers):
                scene.timeline_markers.remove(m)

        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            name = parts[0]
            try:
                frame = int(parts[1])
            except Exception:
                try:
                    frame = int(float(parts[1]))
                except Exception:
                    continue

            if merge_mode == 'APPEND':
                existing = scene.timeline_markers.get(name)
                if existing:
                    existing.frame = frame
                    continue

            scene.timeline_markers.new(name, frame=frame)

        return {'FINISHED'}
