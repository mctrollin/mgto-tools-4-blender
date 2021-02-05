import sys
import math
from datetime import datetime
import bpy
from bpy.types import Panel
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_manager_overlays import MGTOOLSOverlayManager

class MGTOOLS_PT_rigging(Panel):
    bl_idname = "MGTOOLS_PT_rigging"
    bl_label = "Rigging"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        col = l.column()

        if None == bpy.context.scene:
            col.label(text="Scene properties not yet initialized", icon='ERROR', )
            return

        mgtools_props_scene = bpy.context.scene.mgtools

        box = col.box()
        box.label(text="Bone Snapshot Tool")
        if 'EDIT_ARMATURE' != bpy.context.mode:
            box.label(text="EDIT_ARMATURE mode required", icon='ERROR', )
        else:
            if 0 >= len(bpy.context.selected_objects):
                box.label(text="Nothing actively selected", icon='ERROR', )
            else:
                row = box.row()
                row.label(text="Bones prefix")
                row.prop(mgtools_props_scene, 'p_rigging_bone_name_prefix', text="")
                box.prop(mgtools_props_scene, 'p_rigging_add_root_bone')
                box.prop(mgtools_props_scene, 'p_rigging_add_rotation_constraints_to_cloned_bones')
                box.operator('mgtools.rigging_extract_clone_bones', text="Make Bones Snapshot")

                
        
        box = col.box()
        box.label(text="Retarget bone constraints")
        box.prop(mgtools_props_scene, 'p_rigging_constraints_retarget_target_armature', text = "Target",)
        box.operator('mgtools.rigging_constraints_retarget', text="Retarget Constraints")


class MGTOOLS_PT_weighting(Panel):
    bl_idname = "MGTOOLS_PT_weighting"
    bl_label = "Weighting"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        l.active = False
        col = l.column()
       
        # Draw vertex weights --------------------------------------------------------
        if None == bpy.context.object:
            col.label(text="Object properties not yet initialized", icon='ERROR', )
            return

        l.active = True

        # check properties attribute
        if False == hasattr(bpy.context.object, 'mgtools'):
            col.label(text="Object has no 'mgtools' property", icon='ERROR', )
            return

        mgtools_props_obj = bpy.context.object.mgtools

        col.prop(mgtools_props_obj, 'p_weightdisplay_isenabled', toggle=True,)
        col.prop(mgtools_props_obj, 'p_weightdisplay_point_radius')
        # col.prop(mgtools_props_obj, 'p_weightdisplay_point_size')
        # col.prop(mgtools_props_obj, 'p_weightdisplay_global_alpha')

        col = l.column()
        col.prop(bpy.context.preferences.view, "use_weight_color_range", toggle=True, text="Use custom weight colors")
        # col.separator()
        

        # Infos --------------------------------------------------------
        l.separator()

        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()

        if None == meshobj:
            col.label(text="No mesh object active and selected", icon='INFO', )
            return
        
        box = l.box()
        box.scale_y = 0.5
        box.label(text="{} ({})".format(meshobj.name, meshobj.type), )

        verts_selected = MGTOOLS_functions_helper.get_selected_verts(meshobj)
        box.label(text="v:{}/{} | vg:{}".format(len(verts_selected), len(meshobj.data.vertices), len(meshobj.vertex_groups) ))

        if 'WEIGHT_PAINT' != meshobj.mode:
            col.label(text="Weight paint mode needs to be active", icon='INFO', )
            return


        # Weight tools --------------------------------------------------------

        # create vertex groups for selected bones
        row = l.row()
        row.operator('mgtools.weighting_create_vertex_groups_for_selected_bones', text="Create missing VGs for sel. bones")

        # set weight shortcuts
        row = l.row()
        # row.scale_x = 0.1
        # row.scale_y = 0.5
        row.operator('mgtools.weighting_set_weights_to_0', text="0")
        row.operator('mgtools.weighting_set_weights_to_01', text=".1")
        row.operator('mgtools.weighting_set_weights_to_025', text=".25")
        row.operator('mgtools.weighting_set_weights_to_05', text=".5")
        row.operator('mgtools.weighting_set_weights_to_075', text=".75")
        row.operator('mgtools.weighting_set_weights_to_09', text=".9")
        row.operator('mgtools.weighting_set_weights_to_1', text="1")


        # set weight to
        row = l.row()
        row.prop(bpy.context.scene.tool_settings.unified_paint_settings, 'weight', text="")
        row.operator('mgtools.weighting_set_weights', text="Set")

        # add / subtract weight
        row = l.row()
        row.prop(mgtools_props_obj, 'p_weightedit_add_amount', text="")
        row.operator('mgtools.weighting_add_weights', text="+")
        row.operator('mgtools.weighting_subtract_weights', text="-")

        row = l.row()
        row.operator('mgtools.weighting_flatten_weights', text="Flatten")
       
        l.separator()

        # default default
        l.template_list("UI_UL_list", "testlist_id_default", meshobj, "vertex_groups", meshobj.vertex_groups, "active_index", item_dyntip_propname="", rows=5, maxrows=5, type='COMPACT', columns=9, sort_reverse=False, sort_lock=False)
        
        # custom basic
        l.template_list("MGTOOLS_UL_vgroups", "testlist_id_custom_basic", meshobj, "vertex_groups", meshobj.vertex_groups, "active_index", item_dyntip_propname="", rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)

        l.separator()

        # remove weakest influences up to allowed maximum influences count
        row = l.row()
        row.prop(mgtools_props_obj, 'p_weightedit_max_influences', text="")
        row.operator('mgtools.weighting_set_max_influences', text="Limit influence count")

        # remove influences below threshold
        row = l.row()
        row.prop(mgtools_props_obj, 'p_weightedit_min_weight', text="")
        row.operator('mgtools.weighting_set_min_influence', text="Clear influences below")

        # mirror weights
        box_mirror = l.box()
        box_mirror.label(text="Mirror", )
        row = box_mirror.row()
        row.prop(mgtools_props_obj, 'p_weightedit_mirror_all_groups',)
        row.prop(mgtools_props_obj, 'p_weightedit_mirror_use_topology',)
        box_mirror.operator('mgtools.weighting_quick_mirror', text="Mirror X")


class MGTOOLS_PT_animation(Panel):
    bl_idname = "MGTOOLS_PT_animation"
    bl_label = "Animation"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        # l.active = False
        col = l.column()

        if None == bpy.context.scene:
            col.label(text="Scene properties not yet initialized", icon='ERROR', )
            return

        mgtools_props_scene = bpy.context.scene.mgtools

        flow = l.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)

        # auto update motion paths
        row = flow.row(align=True)
        row.operator('mgtools.animation_auto_update_motion_paths', icon='TIME', text='Auto Update Motion Paths')
        if mgtools_props_scene.p_motionpaths_is_auto_update_active :
            row.prop(mgtools_props_scene, 'p_motionpaths_is_auto_update_active', text = "", icon='CANCEL')

        # copy animation data
        anim_copy_box = col.box()
        anim_copy_box.label(text="Animation Data Copy",)
        anim_copy_box.prop(mgtools_props_scene, 'p_animation_copy_data_source', text = "Source",)
        anim_copy_box.prop(mgtools_props_scene, 'p_animation_copy_data_target', text = "Target",)
        anim_copy_box.operator('mgtools.animation_copy_animation_data', text='Copy animation data')

class MGTOOLS_PT_object(Panel):
    bl_idname = "MGTOOLS_PT_object"
    bl_label = "Object"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        col = l.column()

        if None == bpy.context.object:
            col.label(text="Object properties not yet initialized", icon='ERROR', )
            return

        mgtools_props_obj = bpy.context.object.mgtools

        # pivot tools
        pivot_box = col.box()
        pivot_box.label(text="Pivot")
        pivot_box.operator('mgtools.object_pivot_copy', text="Copy Active Pivot")

        # parent tools
        parent_box = col.box()
        parent_box.label(text="Parent")
        if None != context.view_layer.objects.active:
            parent_box.operator('mgtools.object_parent_set', text="Parent to: {}".format(context.view_layer.objects.active.name))
        parent_box.operator('mgtools.object_parent_clear', text="Clear")

        # transform helper
        transform_box = col.box()
        transform_box.label(text="Transforms")
        transform_box.prop(mgtools_props_obj, "p_transforms_world_location")
        transform_box.prop(mgtools_props_obj, "p_transforms_local_location")
        # transform_box.prop(mgtools_props_obj, "p_transforms_world_rotation") # not required, use default blender prop
        transform_box.prop(mgtools_props_obj, "p_transforms_local_rotation")

        # snapshot tools
        snap_box = col.box()
        snap_box.label(text="Snapshots")
        snap_box.prop(mgtools_props_obj, 'p_snapshot_use_name_prefix')
        snap_box.prop(mgtools_props_obj, 'p_snapshot_name_prefix')
        snap_box.prop(mgtools_props_obj, 'p_snapshot_merge_objects')
        snap_box.prop(mgtools_props_obj, 'p_snapshot_frame_start')
        snap_box.prop(mgtools_props_obj, 'p_snapshot_frame_end')

        snap_box.operator('mgtools.object_snapshot', text="Make Range Snapshots")

class MGTOOLS_PT_renaming(Panel):
    bl_idname = "MGTOOLS_PT_renaming"
    bl_label = "Renaming"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        col = l.column()

        # get scene props
        if None == bpy.context.scene:
            col.label(text="Scene properties not yet initialized", icon='ERROR', )
            return
        mgtools_props_scene = bpy.context.scene.mgtools

        # rename using a mapping file
        mapping_box = col.box()
        mapping_box.label(text="Rename with mapping")

        mapping_box.prop(mgtools_props_scene, 'p_rename_mapping_file_path')
        mapping_box.prop(mgtools_props_scene, 'p_rename_mapping_inverse')

        mapping_box.operator('mgtools.rename_bones', text="Rename Bones")
        mapping_box.operator('mgtools.rename_vertexgroups', text="Rename Vertex Groups")

        tools_box = col.box()
        tools_box.label(text="Tools")
        tools_box.operator('mgtools.rename_print_bones', text="Output bone names")

        # get object props
        # if None == bpy.context.object:
        #     col.label(text="Object properties not yet initialized", icon='ERROR', )
        #     return
        # mgtools_props_obj = bpy.context.object.mgtools
        

       

class MGTOOLS_PT_io(Panel):
    bl_idname = "MGTOOLS_PT_io"
    bl_label = "I/O"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        col = l.column()

        if None == bpy.context.scene:
            col.label(text="Scene properties not yet initialized", icon='ERROR', )
            return

        mgtools_props_scene = bpy.context.scene.mgtools

        # main options
        main_options_box = col.box()
        row = main_options_box.row()
        row.label(text="Forward")
        row.prop(mgtools_props_scene, "p_io_export_axis_forward", text="",)
        row.label(text="Up")
        row.prop(mgtools_props_scene, "p_io_export_axis_up", text="")
        row = main_options_box.row()
        row.label(text="Bone Primary Axis")
        row.prop(mgtools_props_scene, "p_io_export_primary_bone_axis", text="",)
        row.label(text="Bone Secondary Axis")
        row.prop(mgtools_props_scene, "p_io_export_secondary_bone_axis", text="")
        main_options_box.prop(mgtools_props_scene, "p_io_export_use_mesh_modifiers",)
        
        pivot_options_box = col.box()
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_include_pivot_dummy",)
        if True == mgtools_props_scene.p_io_export_include_pivot_dummy:
            pivot_options_box.prop(mgtools_props_scene, "p_io_export_include_pivot_dummy_if_required",)
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_set_pivots_to_dummy",)
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_from_origin",)
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_alter_rotation",)
        if True == mgtools_props_scene.p_io_export_alter_rotation:
            pivot_options_box.prop(mgtools_props_scene, "p_io_export_rotation",)
        
        merge_options_box = col.box()
        merge_options_box.prop(mgtools_props_scene, "p_io_export_merge",)
        # if True == mgtools_props_scene.p_io_export_merge:
        #     row = merge_options_box.row()

        naming_options_box = col.box()
        row = naming_options_box.row()
        row.label(text="Pre / Posfix")
        row.prop(mgtools_props_scene, "p_io_export_name_prefix", text="")
        row.prop(mgtools_props_scene, "p_io_export_name_posfix", text="")

        # main_options_box.prop(mgtools_props_scene, "ignore_hidden_objects", toggle=True)
        # main_options_box.prop(mgtools_props_scene, "ignore_hidden_collections", toggle=True)

      

        # selection export -------------------------------------------
        # > path options
        box = col.box()
        # label
        box.label(text="Selection export")
        # > path options
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_filepath", text="")
        row.operator("mgtools.io_open_selection_export_folder", text="", icon='VIEWZOOM')
        # > export
        box.operator('mgtools.io_export_selection', text="Export Selection")


        # collection (batch-) export -------------------------------------------
        # filter options
        box = col.box()
        # label
        box.label(text="Collections batch export")
        # > filter
        row = box.row()
        row.label(text="Filter: Collections")
        row.prop(mgtools_props_scene, "p_io_export_prefix_filter_collection", text="")
        row = box.row()
        row.label(text="Filter: Pivots")
        row.prop(mgtools_props_scene, "p_io_export_prefix_filter_pivot", text="")
        # > export file name options
        row = box.row()
        row.label(text="File Prefix")
        row.prop(mgtools_props_scene, "p_io_export_filename_prefix", text="")
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_filename_include_blendfilename")
        # > path options
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_folder_collections", text="")
        row.operator("mgtools.io_open_collections_export_folder", text="", icon='VIEWZOOM')
        # > export
        box.operator('mgtools.io_export_collections', text="Export Collections")


        # animations (batch-) export -------------------------------------------
        box = col.box()
        # label
        box.label(text="Animations batch export")
        # > settings
        box.prop(mgtools_props_scene, "p_io_export_actions_reference_override",)
        box.prop(mgtools_props_scene, "p_io_export_use_relative_frameranges",)
        row = box.row()
        row.label(text="Prefix")
        row.prop(mgtools_props_scene, "p_io_export_animation_file_prefix", text="")
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_folder_animations", text="")
        row.operator("mgtools.io_open_collections_export_folder", text="", icon='VIEWZOOM')
        # > export
        box.operator('mgtools.io_export_animations', text="Export Animations")


        # hitboxes (batch-) export -------------------------------------------
        box = col.box()
        # label
        box.label(text="Hitboxes batch export")
        # > filter
        row = box.row()
        row.label(text="Filter: Collections")
        row.prop(mgtools_props_scene, "p_io_export_prefix_filter_collection_hitboxes", text="")
        # row = box.row()
        # row.label(text="Filter: Pivots")
        # row.prop(mgtools_props_scene, "p_io_export_prefix_filter_pivot", text="")
        # > export
        box.operator('mgtools.io_export_hitboxes', text="Export Hitboxes")


class MGTOOLS_PT_misc(Panel):
    bl_idname = "MGTOOLS_PT_misc"
    bl_label = "Misc"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout
        col = l.column()
        col.label(text="Misc Stuff...")

class MGTOOLS_PT_sandbox(Panel):
    bl_idname = "MGTOOLS_PT_sandbox"
    bl_label = "Sandbox"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout

        col = l.column()
        col.label(text="Only debug and test stuff!", icon='ERROR', )

        col.operator("mgtools.sandbox_debug1", text="Debug Test Slot 1",)

        

class MGTOOLS_PT_about(Panel):
    bl_idname = "MGTOOLS_PT_about"
    bl_label = "About"
    bl_category = "mgtools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        l = self.layout

        box = l.column()
        box.label(text="MGTO tools v0.6.1") # check also version in __init__
        box.label(text="by Till - rollin - Maginot")
        box.label(text="(C) 2021")

        python_version_info = sys.version_info
        box = l.column()
        box.label(text=("Using Python: {}.{}.{}".format(python_version_info.major, python_version_info.minor, python_version_info.micro)))


# Layout extensions #############################################################################################

weights_list_refresh_timer = datetime.now()
weights_list_filter_flags = []
weights_list_filter_sorting = []

# vertex groups list for weights
class MGTOOLS_UL_vgroups(bpy.types.UIList):
    # required for filtering
    VGROUP_EMPTY = 1 << 0

    

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot_vg = item

        selected_verts_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(ob)
        weight_average = MGTOOLS_functions_helper.get_weight_average(ob, slot_vg.index, selected_verts_indices)

        # 'DEFAULT' and 'COMPACT'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if slot_vg:
                row = layout.row()
                row.prop(slot_vg, "name", text="", emboss=False, icon_value=icon)
                row.label(text=str(round(weight_average,2)))
                if(0 >= weight_average):
                    row.enabled = False
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID'
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    # this is not necessary. The default filtering works and is a lot faster then the code below but does not sort and filter the way we want
    def filter_items(self, context, data, propname):
        vgroups = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # reduce update rate to improve performance
        global weights_list_refresh_timer
        global weights_list_filter_flags
        global weights_list_filter_sorting

        deltatime = (datetime.now() - weights_list_refresh_timer).total_seconds()
        if 2 > deltatime:
            return weights_list_filter_flags, weights_list_filter_sorting
        weights_list_refresh_timer = datetime.now()

        # Filtering ------------------------------
        weights_list_filter_flags = [self.bitflag_filter_item] * len(vgroups)
        weights_list_filter_sorting = [] * len(vgroups)

        # Prepare average-weight-per-vertex-group list
        weight_averages = []
        selected_verts_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(data)
        for idx, vg in enumerate(vgroups):
            weight_average = MGTOOLS_functions_helper.get_weight_average(data, idx, selected_verts_indices)
            weight_averages.append((idx, weight_average))
            # Filter by zero average weight
            if 0 < weight_average:
                weights_list_filter_flags[idx] |= self.VGROUP_EMPTY
            else:
                weights_list_filter_flags[idx]  &= ~self.bitflag_filter_item

        # Filter by name
        if self.filter_name:
            weights_list_filter_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, vgroups, "name", reverse=False)

        # Sorting ------------------------------
        weights_list_filter_sorting = helper_funcs.sort_items_helper(weight_averages, lambda e: e[1], True)
        
        return weights_list_filter_flags, weights_list_filter_sorting
    
