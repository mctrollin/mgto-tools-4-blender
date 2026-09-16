# pyright: reportInvalidTypeForm=false

import bpy
import bmesh
import math
import bl_math
from bpy.types import Operator
from . mgtools_manager_overlays import MGTOOLSOverlayManager
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . import mgtools_functions_log

_WEIGHTING_MESH_MODES = {'OBJECT', 'WEIGHT_PAINT'}


def _weighting_context_guard(context, require_active_group=False):
    obj = context.view_layer.objects.active
    if obj is None:
        return None, "No active mesh object"
    if obj.type != 'MESH':
        return None, "The active object is not a mesh"
    if obj.mode not in _WEIGHTING_MESH_MODES:
        return None, "This operation requires Object or Weight Paint mode"
    if require_active_group and obj.vertex_groups.active is None:
        return None, "No active vertex group"
    return obj, None


def _cancel_invalid_weighting_context(operator, context, require_active_group=False):
    obj, error = _weighting_context_guard(context, require_active_group)
    if error is not None:
        operator.report({'ERROR'}, error)
        return None
    return obj


class MGTOOLS_weighting_operator:
    @classmethod
    def poll(cls, context):
        obj, error = _weighting_context_guard(context)
        return obj is not None and error is None


class MGTOOLS_OT_weighting_rebuild_active_vertex_group(Operator):
    bl_idname = "mgtools.weighting_rebuild_active_vertex_group"
    bl_label = "Rebuild Active Vertex Group Order"
    bl_description = "Rebuild the vertex-group collection with the active group at the top or bottom"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Position",
        items=(
            ('TOP', "Top", "Rebuild with the active vertex group at the top"),
            ('BOTTOM', "Bottom", "Rebuild with the active vertex group at the bottom"),
        ),
        default='TOP',
    )

    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == 'MESH' and obj.vertex_groups.active is not None

    def execute(self, context):
        if not MGTOOLS_functions_macros.rebuild_active_vertex_group_to(self.direction):
            self.report({'ERROR'}, "Could not rebuild the vertex-group order")
            return {'CANCELLED'}
        return {'FINISHED'}

# show colored vertices
class MGTOOLS_OT_weighting_show_weights(Operator):
    bl_idname =  "mgtools.weighting_show_weights"
    bl_label = "Show vertex weights"
    bl_description = "Draw vertex weights as dots over vertices"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        MGTOOLSOverlayManager.init()
        return {'FINISHED'}
# hide colored vertices
class MGTOOLS_OT_weighting_hide_weights(Operator):
    bl_idname =  "mgtools.weighting_hide_weights"
    bl_label = "Hide vertex weights"
    bl_description = "Stops drawing vertex weights as dots over vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLSOverlayManager.deinit()
        return {'FINISHED'}

# set weight
class MGTOOLS_OT_weighting_set_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights"
    bl_label = "Set vertex weights"
    bl_description = "Set a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        success = MGTOOLS_functions_macros.set_weights_to_selected_mesh(
            context.scene.tool_settings.weight_paint.unified_paint_settings.weight,
            'REPLACE',
            context.scene.tool_settings.use_auto_normalize,
        )
        if not success:
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# add weight
class MGTOOLS_OT_weighting_offset_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_offset_weights"
    bl_label = "Add or subtract vertex weights"
    bl_description = "Add or subtract a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    amount: bpy.props.FloatProperty(
        name = 'amount',
        default = 0
        )

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        amount_abs = math.fabs(self.amount)
        mode = 'ADD' if self.amount > 0 else 'SUBTRACT'
        success = MGTOOLS_functions_macros.set_weights_to_selected_mesh(
            amount_abs,
            mode,
            context.scene.tool_settings.use_auto_normalize,
        )
        if not success:
            self.report({'ERROR'}, "Could not modify vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}

# copy weights - set vertex group target
class MGTOOLS_OT_weighting_copy_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_copy_weights"
    bl_label = "Copy vertex weights"
    bl_description = "Store the active vertex group's weights for pasting to another vertex group"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        meshobj = _cancel_invalid_weighting_context(self, context, True)
        if meshobj is None:
            return {'CANCELLED'}
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        # get vertex group
        activeVG = meshobj.vertex_groups.active
        if None == activeVG:
            print("No active vertex group")
            return {'CANCELLED'}
        
        mgtools_props_obj = context.scene.mgtools
        mgtools_props_obj.p_weightedit_copy_vg = activeVG.name

        return {'FINISHED'}

class MGTOOLS_OT_weighting_paste_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_paste_weights"
    bl_label = "Paste vertex weights"
    bl_description = "Add the stored vertex weights to the active vertex group on selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        meshobj = _cancel_invalid_weighting_context(self, context, True)
        if meshobj is None:
            return {'CANCELLED'}
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        # get vertex group
        activeVG = meshobj.vertex_groups.active
        if None == activeVG:
            print("No active vertex group")
            return {'CANCELLED'}
        
        mgtools_props_obj = context.scene.mgtools

        # select vertex group by name
        vg_from = None
        for vg in meshobj.vertex_groups:
            if vg.name == mgtools_props_obj.p_weightedit_copy_vg:
                vg_from = vg

        if None == vg_from:
            print("No vertex group defined to copy weights from")
            return {'CANCELLED'}

        vg_to = activeVG

        # get selected vertices
        selected_vert_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)

        mirror_enabled = MGTOOLS_functions_helper.has_mirror_enabled(meshobj)

        if mirror_enabled:
            values = {}
            for index in selected_vert_indices:
                try:
                    source_weight = vg_from.weight(index)
                except Exception:
                    continue
                target_weight = 0.0
                try:
                    target_weight = vg_to.weight(index)
                except Exception:
                    pass
                values[index] = target_weight + source_weight
            meshobj.vertex_groups.active_index = vg_to.index
            if not MGTOOLS_functions_macros.weight_set_vertices(meshobj, values):
                self.report({'ERROR'}, "Could not paste mirrored vertex weights")
                return {'CANCELLED'}
            if bpy.context.scene.tool_settings.use_auto_normalize:
                if not MGTOOLS_functions_macros.renormalize_weights():
                    self.report({'ERROR'}, "Could not normalize pasted weights")
                    return {'CANCELLED'}
        else:
            if not MGTOOLS_functions_macros.transfer_weights_from_selection(vg_from, vg_to, meshobj, selected_vert_indices, bpy.context.scene.tool_settings.use_auto_normalize):
                self.report({'ERROR'}, "Could not paste vertex weights")
                return {'CANCELLED'}

        return {'FINISHED'}


class MGTOOLS_OT_weighting_copy_vertex_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname = "mgtools.weighting_copy_vertex_weights"
    bl_label = "Copy Vertex Weights"
    bl_description = "Copy all vertex-group weights from the active selected vertex to every other selected vertex"
    bl_options = {'REGISTER'}

    def execute(self, context):
        meshobj = _cancel_invalid_weighting_context(self, context, False)
        if meshobj is None:
            return {'CANCELLED'}
        if None == meshobj:
            self.report({'WARNING'}, "No mesh object selected")
            return {'CANCELLED'}

        selected_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)
        if 2 > len(selected_indices):
            self.report({'WARNING'}, "Select a source vertex and at least one destination vertex")
            return {'CANCELLED'}

        mode_cached = meshobj.mode
        active_group_cached = meshobj.vertex_groups.active_index
        tool_settings = context.scene.tool_settings
        auto_normalize_cached = tool_settings.use_auto_normalize
        source_index = None

        try:
            # Blender stores the active mesh element in edit-mesh selection history.
            # The active/last-selected vertex is the source for this operation.
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(meshobj.data)
            active_element = bm.select_history.active
            if isinstance(active_element, bmesh.types.BMVert) and active_element.select:
                source_index = active_element.index
        finally:
            if meshobj.mode != mode_cached:
                bpy.ops.object.mode_set(mode=mode_cached)

        if source_index is None or source_index not in selected_indices:
            self.report({'WARNING'}, "The active selected element must be a vertex")
            return {'CANCELLED'}

        destination_indices = [index for index in selected_indices if index != source_index]
        values_by_group = {}
        for vertex_group in meshobj.vertex_groups:
            try:
                source_weight = vertex_group.weight(source_index)
            except RuntimeError:
                source_weight = 0.0
            values_by_group[vertex_group.index] = {index: source_weight for index in destination_indices}

        mirror_enabled = MGTOOLS_functions_helper.has_mirror_enabled(meshobj)

        try:
            # Assign groups independently so automatic normalization cannot alter
            # the source values or intermediate destination assignments.
            tool_settings.use_auto_normalize = False
            for group_index, values in values_by_group.items():
                meshobj.vertex_groups.active_index = group_index
                if mirror_enabled:
                    if not MGTOOLS_functions_macros.weight_set_vertices(meshobj, values):
                        self.report({'ERROR'}, "Could not copy mirrored vertex weights")
                        return {'CANCELLED'}
                else:
                    meshobj.vertex_groups[group_index].add(destination_indices, values[destination_indices[0]], 'REPLACE')
        finally:
            tool_settings.use_auto_normalize = auto_normalize_cached
            meshobj.vertex_groups.active_index = active_group_cached

        if auto_normalize_cached:
            if not MGTOOLS_functions_macros.renormalize_weights():
                self.report({'ERROR'}, "Could not normalize copied weights")
                return {'CANCELLED'}

        return {'FINISHED'}


# set weight to 0.0
class MGTOOLS_OT_weighting_set_weights_to_0(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_0"
    bl_label = "Set vertex weights to 0"
    bl_description = "Set weigh of selected vertices to 0"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 0.1
class MGTOOLS_OT_weighting_set_weights_to_01(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_01"
    bl_label = "Set vertex weights to 0.1"
    bl_description = "Set weigh of selected vertices to 0.1"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.1, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 0.25
class MGTOOLS_OT_weighting_set_weights_to_025(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_025"
    bl_label = "Set vertex weights to 0.25"
    bl_description = "Set weigh of selected vertices to 0.25"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.25, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 0.5
class MGTOOLS_OT_weighting_set_weights_to_05(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_05"
    bl_label = "Set vertex weights to 0.5"
    bl_description = "Set weigh of selected vertices to 0.5"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.5, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 0.75
class MGTOOLS_OT_weighting_set_weights_to_075(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_075"
    bl_label = "Set vertex weights to 0.75"
    bl_description = "Set weigh of selected vertices to 0.75"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.75, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 0.9
class MGTOOLS_OT_weighting_set_weights_to_09(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_09"
    bl_label = "Set vertex weights to 0.9"
    bl_description = "Set weigh of selected vertices to 0.9"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.9, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}
# set weight to 1.0
class MGTOOLS_OT_weighting_set_weights_to_1(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_1"
    bl_label = "Set vertex weights to 1"
    bl_description = "Set weigh of selected vertices to 1"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.set_weights_to_selected_mesh(1, 'REPLACE', context.scene.tool_settings.use_auto_normalize):
            self.report({'ERROR'}, "Could not set vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}

# mirror all weights from all vertices across a selected local axis
class MGTOOLS_OT_weighting_quick_mirror(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_quick_mirror"
    bl_label = "Quick Mirror"
    bl_description = "Mirror all weights across the selected axis and direction"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        meshobj = _cancel_invalid_weighting_context(self, context, False)
        if None == meshobj:
            return {'CANCELLED'}

        mgtools_props_obj = context.scene.mgtools
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[mgtools_props_obj.p_weightedit_mirror_axis]
        destination_positive = mgtools_props_obj.p_weightedit_mirror_direction == 'NEGATIVE_TO_POSITIVE'
        selection_cached = [False for i in range(len(meshobj.data.vertices))]

        with mgtools_functions_log.log_timing("weighting.quick_mirror"):
            # Select the destination side. vertex_group_mirror copies from the
            # opposite side into the selected side.
            for vert in meshobj.data.vertices:
                selection_cached[vert.index] = vert.select
                coordinate = vert.co[axis_index]
                vert.select = coordinate > 0.0 if destination_positive else coordinate < 0.0

            try:
                bpy.ops.object.vertex_group_mirror(
                    mirror_weights=True,
                    flip_group_names=True,
                    all_groups=mgtools_props_obj.p_weightedit_mirror_all_groups,
                    use_topology=mgtools_props_obj.p_weightedit_mirror_use_topology)
            finally:
                # Always restore the user's original selection.
                for vert in meshobj.data.vertices:
                    vert.select = selection_cached[vert.index]

        return {'FINISHED'}


# normalize weights of selected vertices
class MGTOOLS_OT_weighting_normalize_weights_groups(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_normalize_weights_groups"
    bl_label = "Normalize vertex weights (All Groups)"
    bl_description = "Normalize weights of selected vertices over all affected vertex groups"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        if _cancel_invalid_weighting_context(self, context, False) is None:
            return {'CANCELLED'}
        if not MGTOOLS_functions_macros.renormalize_weights():
            self.report({'ERROR'}, "Could not normalize vertex weights")
            return {'CANCELLED'}
        return {'FINISHED'}

# set weights of selected vertices to their mean
class MGTOOLS_OT_weighting_average_weights(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_average_weights"
    bl_label = "Average vertex weights"
    bl_description = "Set weights of selected vertices to their mean"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        with mgtools_functions_log.log_timing("MGTOOLS_OT_weighting_average_weights"):
            meshobj = _cancel_invalid_weighting_context(self, context, False)
            if None == meshobj:
                return {'CANCELLED'}

            vgroups = meshobj.vertex_groups

            if 0 >= len(vgroups):
                print("Model has no vertex groups")
                return {'CANCELLED'}
            
            # get selected verts
            selected_verts_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)

            if 0 >= len(selected_verts_indices):
                print("No vertices selected")
                return {'CANCELLED'}

            if len(selected_verts_indices) == 1:
                return {'FINISHED'}

            # properties
            mgtools_props_obj = context.scene.mgtools
            tool_settings = bpy.context.scene.tool_settings
            active_group_cached = vgroups.active_index
            auto_normalize_cached = tool_settings.use_auto_normalize

            # calculate average weights and assign them
            mirror_enabled = MGTOOLS_functions_helper.has_mirror_enabled(meshobj)
            try:
                if mirror_enabled:
                    # Each weight_set() call targets one group. Prevent Blender's
                    # automatic normalization from changing other groups midway.
                    tool_settings.use_auto_normalize = False

                for idx, vg in enumerate(vgroups):
                    weight_average = MGTOOLS_functions_helper.get_weight_average(meshobj, idx, selected_verts_indices)

                    if mirror_enabled:
                        values = {}
                        changed = False
                        for vertex_index in selected_verts_indices:
                            current_weight = 0.0
                            try:
                                current_weight = vg.weight(vertex_index)
                            except Exception:
                                pass
                            target_weight = bl_math.lerp(current_weight, weight_average, mgtools_props_obj.p_weightedit_average_factor)
                            values[vertex_index] = target_weight
                            if not math.isclose(current_weight, target_weight, abs_tol=1e-6):
                                changed = True
                        if not changed:
                            continue
                        meshobj.vertex_groups.active_index = vg.index
                        MGTOOLS_functions_macros.weight_set_vertices(meshobj, values)
                    else:
                        indices_by_weight = {}
                        for vertex_index in selected_verts_indices:
                            current_weight = 0.0
                            try:
                                current_weight = vg.weight(vertex_index)
                            except Exception:
                                pass
                            target_weight = bl_math.lerp(current_weight, weight_average, mgtools_props_obj.p_weightedit_average_factor)
                            if math.isclose(current_weight, target_weight, abs_tol=1e-6):
                                continue
                            indices_by_weight.setdefault(target_weight, []).append(vertex_index)
                        for target_weight, vertex_indices in indices_by_weight.items():
                            vg.add(vertex_indices, target_weight, 'REPLACE')
            finally:
                tool_settings.use_auto_normalize = auto_normalize_cached
                vgroups.active_index = active_group_cached

            if mirror_enabled and auto_normalize_cached:
                if not MGTOOLS_functions_macros.renormalize_weights():
                    self.report({'ERROR'}, "Could not normalize averaged weights")
                    return {'CANCELLED'}

            return {'FINISHED'}

# smooth weights of selected vertices
class MGTOOLS_OT_weighting_smooth_weights_groups(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_smooth_weights_groups"
    bl_label = "Smooth vertex weights (All Groups)"
    bl_description = "Smooth weights of selected vertices over all affected vertex groups"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=1, expand=0.0)
        return {'FINISHED'}

# smooth weights of selected vertices
class MGTOOLS_OT_weighting_smooth_weights_group(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_smooth_weights_group"
    bl_label = "Substract vertex weights (Active Group)"
    bl_description = "Smooth weights of selected vertices over active vertex group"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        if _cancel_invalid_weighting_context(self, context, True) is None:
            return {'CANCELLED'}
        bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=0.5, repeat=1, expand=0.0)
        return {'FINISHED'}

class MGTOOLS_OT_weighting_create_vertex_groups_for_selected_bones(Operator):
    bl_idname =  "mgtools.weighting_create_vertex_groups_for_selected_bones"
    bl_label = "Create vertex groups"
    bl_description = "Create missing vertex groups on active mesh for selected pose bones. Note: make sure to use an armature modifier!"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        # prepare vars
        obj = context.view_layer.objects.active
        selected_bones = context.selected_pose_bones # context.selected_bones
        
        if None == selected_bones or 0 >= len(selected_bones): 
            print("No pose bones selected")
            return {'CANCELLED'}

        bone_names = [bone.name for bone in selected_bones]
        print("obj: {}, bone_names: {}".format(obj, bone_names))
        # create vertex groups
        MGTOOLS_functions_helper.create_vgroups_from_names(obj, bone_names)
        return {'FINISHED'}

class MGTOOLS_OT_weighting_remove_vertex_groups_unused(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_remove_vertex_groups_unused"
    bl_label = "Remove unused vertex groups"
    bl_description = "Remove all vertex groups without any assigned vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        meshobj = _cancel_invalid_weighting_context(self, context, False)
        if None == meshobj:
            return {'CANCELLED'}

        vgroups = meshobj.vertex_groups

        if 0 >= len(vgroups):
            print("Model has no vertex groups")
            return {'CANCELLED'}

        # properties
        mgtools_props_obj = context.scene.mgtools
        
        # prepare vars
        only_unused = mgtools_props_obj.p_weightedit_remove_empty
        include_locked = mgtools_props_obj.p_weightedit_remove_locked

        MGTOOLS_functions_helper.remove_vgroups(meshobj, only_unused, include_locked)


        return {'FINISHED'}


class MGTOOLS_OT_weighting_set_max_influences(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_max_influences"
    bl_label = "Set max influences"
    bl_description = "Keep only the strongest influences up to the maximum allowed amount of total influences per bone"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        obj = _cancel_invalid_weighting_context(self, context, False)
        if obj is None:
            return {'CANCELLED'}
        # properties
        mgtools_props_obj = context.scene.mgtools
        
        # prepare vars
        max_influences = mgtools_props_obj.p_weightedit_max_influences
        armature_modifier = MGTOOLS_functions_helper.get_all_modifier(obj, 'ARMATURE')
        armatures = []
        for amod in armature_modifier:
            armatures.append(amod.object)

        # process
        for armature in armatures:
            MGTOOLS_functions_helper.remove_lowest_weights(obj, armature, max_influences)
        
        # normalize weights --------------
        if True == bpy.context.scene.tool_settings.use_auto_normalize:
            if not MGTOOLS_functions_macros.renormalize_weights():
                self.report({'ERROR'}, "Could not normalize limited weights")
                return {'CANCELLED'}

        return {'FINISHED'}

class MGTOOLS_OT_weighting_set_min_influence(MGTOOLS_weighting_operator, Operator):
    bl_idname =  "mgtools.weighting_set_min_influence"
    bl_label = "Set min influence"
    bl_description = "Remove all influences which are below the minimum required influence per bone"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        obj = _cancel_invalid_weighting_context(self, context, False)
        if obj is None:
            return {'CANCELLED'}
        # properties
        mgtools_props_obj = context.scene.mgtools

        # prepare vars
        weight_threshold = mgtools_props_obj.p_weightedit_min_weight
        armature_modifier = MGTOOLS_functions_helper.get_all_modifier(obj, 'ARMATURE')
        armatures = []
        for amod in armature_modifier:
            armatures.append(amod.object)

        # process
        for armature in armatures:
            MGTOOLS_functions_helper.remove_weights_below_threshold(obj, armature, weight_threshold)

        # normalize weights --------------
        if True == bpy.context.scene.tool_settings.use_auto_normalize:
            if not MGTOOLS_functions_macros.renormalize_weights():
                self.report({'ERROR'}, "Could not normalize thresholded weights")
                return {'CANCELLED'}
        return {'FINISHED'}