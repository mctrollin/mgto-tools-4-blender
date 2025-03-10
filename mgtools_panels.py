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
                box.prop(mgtools_props_scene, 'p_rigging_add_location_constraints_to_cloned_bones')
                box.prop(mgtools_props_scene, 'p_rigging_add_rotation_constraints_to_cloned_bones')
                box.prop(mgtools_props_scene, 'p_rigging_add_scale_constraints_to_cloned_bones')
                box.operator('mgtools.rigging_extract_clone_bones', text="Make Bones Snapshot")

                
        
        box = col.box()
        box.label(text="Retarget object constraints")
        box.prop(mgtools_props_scene, 'p_rigging_object_constraints_retarget_target', text = "Target",)
        box.operator('mgtools.rigging_object_constraints_retarget', text="Retarget Constraints")

        box = col.box()
        box.label(text="Retarget bone constraints")
        box.prop(mgtools_props_scene, 'p_rigging_bone_constraints_retarget_target', text = "Target",)
        box.operator('mgtools.rigging_bone_constraints_retarget', text="Retarget Constraints")

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
        col = l.column()

        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()

        if None == meshobj:
            col.label(text="No active selected mesh!", icon='INFO', )
            return
        
        box = l.box()
        box.scale_y = 0.5
        box.label(text="{} ({})".format(meshobj.name, meshobj.type), )

        verts_selected = MGTOOLS_functions_helper.get_selected_verts(meshobj)
        box.label(text="v: {} / {} | vg: {}".format(len(verts_selected), len(meshobj.data.vertices), len(meshobj.vertex_groups) ))

        if 'WEIGHT_PAINT' != meshobj.mode:
            col.label(text="Requires WeightPaintMode!", icon='INFO', )
            return


        # Weight tools --------------------------------------------------------

        row = l.row()
        box_set_weights = row.box()

        # create vertex groups for selected bones
        row = box_set_weights.row()
        row.operator('mgtools.weighting_create_vertex_groups_for_selected_bones', text="Create missing VGs for sel. bones")

        row = box_set_weights.row()
        row.prop(bpy.context.scene.tool_settings, 'use_auto_normalize', text="Auto Normalize")
        row.operator('mgtools.weighting_normalize_weights_groups', text="Normalize")

        # set weight shortcuts
        
        # row.scale_x = 0.1
        # row.scale_y = 0.5
        row = box_set_weights.row()
        row.operator('mgtools.weighting_set_weights_to_0', text="0")
        row.operator('mgtools.weighting_set_weights_to_01', text=".1")
        row.operator('mgtools.weighting_set_weights_to_025', text=".25")
        row.operator('mgtools.weighting_set_weights_to_05', text=".5")
        row.operator('mgtools.weighting_set_weights_to_075', text=".75")
        row.operator('mgtools.weighting_set_weights_to_09', text=".9")
        row.operator('mgtools.weighting_set_weights_to_1', text="1")

        # set weight to
        row = box_set_weights.row()
        row.prop(bpy.context.scene.tool_settings.unified_paint_settings, 'weight', text="")
        row.operator('mgtools.weighting_set_weights', text="Set")

        # add / subtract weight
        row = box_set_weights.row()
        row.prop(mgtools_props_obj, 'p_weightedit_add_amount', text="")
        op = row.operator('mgtools.weighting_offset_weights', text="+")
        op.amount = mgtools_props_obj.p_weightedit_add_amount
        op = row.operator('mgtools.weighting_offset_weights', text="-")
        op.amount = -1 * mgtools_props_obj.p_weightedit_add_amount

        row = box_set_weights.row()
        op = row.operator('mgtools.weighting_offset_weights', text="+.01")
        op.amount = 0.01
        op = row.operator('mgtools.weighting_offset_weights', text="+.05")
        op.amount = 0.05
        op = row.operator('mgtools.weighting_offset_weights', text="+.1")
        op.amount = 0.1
        row = box_set_weights.row()
        op = row.operator('mgtools.weighting_offset_weights', text="-.01")
        op.amount = -0.01
        op = row.operator('mgtools.weighting_offset_weights', text="-.05")
        op.amount = -0.05
        op = row.operator('mgtools.weighting_offset_weights', text="-.1")
        op.amount = -0.1

        row = box_set_weights.row()
        row.operator('mgtools.weighting_copy_weights', text="copy")
        row.prop(mgtools_props_obj, 'p_weightedit_copy_vg', text="")
        row.operator('mgtools.weighting_paste_weights', text="paste")

        row = box_set_weights.row()
        row.prop(mgtools_props_obj, 'p_weightedit_average_factor', text="")
        row.operator('mgtools.weighting_average_weights', text="Average")

        row = box_set_weights.row()
        row.operator('mgtools.weighting_smooth_weights_group', text="Smooth (Active Group)")
        row.operator('mgtools.weighting_smooth_weights_groups', text="Smooth (All Groups)")
       
        # l.separator()

        # weight list
        box_weight_lists = l.box()
        box_weight_lists.prop(mgtools_props_obj, 'p_weightedit_list_enabled', text="Vertex Groups List View")
        if mgtools_props_obj.p_weightedit_list_enabled:
        
            # default default
            box_weight_lists.template_list("UI_UL_list", "testlist_id_default", meshobj, "vertex_groups", meshobj.vertex_groups, "active_index", item_dyntip_propname="", rows=5, maxrows=5, type='COMPACT', columns=9, sort_reverse=False, sort_lock=False)
            
            # custom basic
            box_weight_lists.template_list("MGTOOLS_UL_vgroups", "testlist_id_custom_basic", meshobj, "vertex_groups", meshobj.vertex_groups, "active_index", item_dyntip_propname="", rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)

        # l.separator()

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
        # box_mirror.label(text="Mirror", )
        row = box_mirror.row()
        row.prop(mgtools_props_obj, 'p_weightedit_mirror_all_groups',)
        row.prop(mgtools_props_obj, 'p_weightedit_mirror_use_topology',)
        box_mirror.operator('mgtools.weighting_quick_mirror', text="Mirror X")

        # remove vertex groups
        box_remove = l.box()
        row = box_remove.row()
        row.prop(mgtools_props_obj, 'p_weightedit_remove_empty', text="Only Empty")
        row.prop(mgtools_props_obj, 'p_weightedit_remove_locked', text="+ Locked")
        box_remove.operator('mgtools.weighting_remove_vertex_groups_unused', text="Remove VGs")

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
        mapping_box.operator('mgtools.rename_fcurves', text="Rename FCurves")

        tools_box = col.box()
        tools_box.label(text="Tools")
        tools_box.operator('mgtools.rename_print_bones', text="Output bone names")
        tools_box.operator('mgtools.rename_mesh_from_object', text="Set Mesh name from Object")

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

        # axis options -------------------------------------------
        axis_options_box = col.box()
        row = axis_options_box.row()
        row.label(text="Forward")
        row.prop(mgtools_props_scene, "p_io_export_axis_forward", text="",)
        row.label(text="Up")
        row.prop(mgtools_props_scene, "p_io_export_axis_up", text="")
        row = axis_options_box.row()
        row.label(text="P Bone Axis")
        row.prop(mgtools_props_scene, "p_io_export_primary_bone_axis", text="",)
        row.label(text="S Bone Axis")
        row.prop(mgtools_props_scene, "p_io_export_secondary_bone_axis", text="")

        # scale options -------------------------------------------
        scale_options_box = col.box()
        row = scale_options_box.row()
        row.prop(mgtools_props_scene, "p_io_export_scale", text="")
        row.prop(mgtools_props_scene, "p_io_export_scale_apply_options", text="")
        row.prop(mgtools_props_scene, "p_io_export_apply_unit_scale",)

        row = scale_options_box.row()
        row.prop(mgtools_props_scene, "p_io_export_use_space_transform",)

        # pivot options -------------------------------------------
        pivot_options_box = col.box()
        pivot_options_box.label(text="Pivot")
        row = pivot_options_box.row()
        row.label(text="Filter:")
        row.prop(mgtools_props_scene, "p_io_export_prefix_filter_pivot", text="")
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_include_pivot_dummy",)
        if True == mgtools_props_scene.p_io_export_include_pivot_dummy:
            pivot_options_box.prop(mgtools_props_scene, "p_io_export_include_pivot_dummy_if_required",)
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_set_pivots_to_dummy",)
        row = pivot_options_box.row()
        row.label(text="Reset:")
        row.prop(mgtools_props_scene, "p_io_export_pivot_reset_location", text="location")
        row.prop(mgtools_props_scene, "p_io_export_pivot_reset_rotation", text="rotation")
        row.prop(mgtools_props_scene, "p_io_export_pivot_reset_scale", text="scale")
        if True == mgtools_props_scene.p_io_export_pivot_reset_rotation:
            pivot_options_box.prop(mgtools_props_scene, "p_io_export_rotation",)
        pivot_options_box.prop(mgtools_props_scene, "p_io_export_pivot_dummy_disable_constraints",)

        # helper options -------------------------------------------
        helper_options_box = col.box()
        helper_options_box.label(text="Helper")
        helper_options_box.prop(mgtools_props_scene, "p_io_export_helper_strip_dotnumbers",)

        # mesh options -------------------------------------------
        mesh_options_box = col.box()
        mesh_options_box.label(text="Mesh")
        # currently modifiers are always applied for multiple export features requiring it
        # mesh_options_box.prop(mgtools_props_scene, "p_io_export_use_mesh_modifiers",)
        mesh_options_box.prop(mgtools_props_scene, "p_io_export_use_mesh_modifiers_armature",)
        mesh_options_box.prop(mgtools_props_scene, "p_io_export_mesh_smooth_type",)

        mesh_options_box2 = mesh_options_box.box()
        mesh_options_box2.label(text="Clones")
        row = mesh_options_box2.row()
        row.label(text="Clone Filter:")
        row.prop(mgtools_props_scene, "p_io_export_clone_meshes_filter", text="")
        mesh_options_box2.prop(mgtools_props_scene, "p_io_export_combine_meshes", text="Combine Cloned Meshes")
        if True == mgtools_props_scene.p_io_export_combine_meshes:
            row = mesh_options_box2.row()
            row.label(text="Combine Filter:")
            row.prop(mgtools_props_scene, "p_io_export_combine_meshes_filter", text="")
        row = mesh_options_box2.row()
        row.prop(mgtools_props_scene, "p_io_export_objectname_prefix", text="Pre")
        row.prop(mgtools_props_scene, "p_io_export_objectname_postfix", text="Pos")
        mesh_options_box2.prop(mgtools_props_scene, "p_io_export_material_override",)
        mesh_options_box2.prop(mgtools_props_scene, "p_io_export_armature_replacement",)
        mesh_options_box2.prop(mgtools_props_scene, "p_io_export_weights_limit",)

        mesh_options_box3 = mesh_options_box.box()
        mesh_options_box3.prop(mgtools_props_scene, "p_io_export_vgroups_rename",)
        if True == mgtools_props_scene.p_io_export_vgroups_rename:
            mesh_options_box3.prop(mgtools_props_scene, "p_io_export_vgroups_rename_mapping_file_path",)
            mesh_options_box3.prop(mgtools_props_scene, "p_io_export_vgroups_rename_mapping_inverse",)

        # main_options_box.prop(mgtools_props_scene, "ignore_hidden_objects", toggle=True)
        # main_options_box.prop(mgtools_props_scene, "ignore_hidden_collections", toggle=True)

        # armature options -------------------------------------------
        armature_options_box = col.box()
        armature_options_box.label(text="Armature")
        row = armature_options_box.row()
        row.label(text="Rename:")
        row.prop(mgtools_props_scene, "p_io_export_armature_rename", text="")

        # animation options -------------------------------------------
        animation_options_box = col.box()
        animation_options_box.label(text="Animation")
        animation_options_box.prop(mgtools_props_scene, "p_io_export_animation_mode", text="Mode")
        if 'OFF' == mgtools_props_scene.p_io_export_animation_mode:
            animation_options_box.prop(mgtools_props_scene, "p_io_export_frame",)
        else:
            animation_options_box.prop(mgtools_props_scene, "p_io_export_animation_bake_anim_simplify_factor",)
        if 'STRIPS' == mgtools_props_scene.p_io_export_animation_mode:
            animation_options_box.prop(mgtools_props_scene, "p_io_export_animation_use_relative_frameranges",)
        if 'MARKERS' == mgtools_props_scene.p_io_export_animation_mode:
            animation_options_box.prop(mgtools_props_scene, "p_io_export_animation_marker_start", text="Start")
            animation_options_box.prop(mgtools_props_scene, "p_io_export_animation_marker_end", text="End")

        # filename options -------------------------------------------
        box = col.box()
        box.label(text="File name")
        row = box.row()
        row.label(text="Prefix:")
        row.prop(mgtools_props_scene, "p_io_export_filename_prefix", text="")
        row = box.row()
        row.label(text="Prefix Static:")
        row.prop(mgtools_props_scene, "p_io_export_filename_prefix_static", text="")
        row = box.row()
        row.label(text="Prefix Skeletal:")
        row.prop(mgtools_props_scene, "p_io_export_filename_prefix_skeletal", text="")
        row = box.row()
        row.label(text="Prefix Animation:")
        row.prop(mgtools_props_scene, "p_io_export_filename_prefix_animation", text="")
        row = box.row()
        row.label(text="Postfix:")
        row.prop(mgtools_props_scene, "p_io_export_filename_postfix", text="")
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_filename_include_blendfilename")
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_filename_ignore_collection_dot_prefix")


        # collection (batch-) export -------------------------------------------
        # filter options
        box = col.box()
        # label
        box.label(text="Collections batch export")
        # > filter
        row = box.row()
        row.label(text="Filter:")
        row.prop(mgtools_props_scene, "p_io_export_prefix_filter_collection", text="")
        
       
        # > path options
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_folder_collections", text="")
        row.operator("mgtools.io_open_collections_export_folder", text="", icon='WINDOW')
        # > export
        box.operator('mgtools.io_export_collections', text="Export Collections")

        # selection export -------------------------------------------
        # > path options
        box = col.box()
        # label
        box.label(text="Selection export")
        # > path options
        row = box.row()
        row.prop(mgtools_props_scene, "p_io_export_filepath", text="")
        row.operator("mgtools.io_open_selection_export_folder", text="", icon='WINDOW')
        # > export
        box.operator('mgtools.io_export_selection', text="Export Selection")

        # animations (batch-) export -------------------------------------------
        # box = col.box()
        # # label
        # box.label(text="Animations batch export")
        # # > settings
        # box.prop(mgtools_props_scene, "p_io_export_animation_actions_reference_override",)
        # box.prop(mgtools_props_scene, "p_io_export_animation_use_relative_frameranges",)
        # row = box.row()
        # row.label(text="Prefix")
        # row.prop(mgtools_props_scene, "p_io_export_filename_prefix_animation", text="")
        # row = box.row()
        # row.prop(mgtools_props_scene, "p_io_export_animation_folder", text="")
        # row.operator("mgtools.io_open_collections_export_folder", text="", icon='VIEWZOOM')
        # # > export
        # box.operator('mgtools.io_export_animations', text="Export Animations")


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

        # get scene props
        if None == bpy.context.scene:
            col.label(text="Scene properties not yet initialized", icon='ERROR', )
            return
        mgtools_props_scene = bpy.context.scene.mgtools

        col.label(text="Misc Stuff...")


        ### particle hair -----------------------------------
        particlehair_box = col.box()
        # label
        particlehair_box.label(text="Particle Hair")

        # > to mesh
        row = particlehair_box.row()
        row.prop(mgtools_props_scene, "p_particle_hair_to_mesh_thickness", text="Thickness")
        row = particlehair_box.row()
        row.prop(mgtools_props_scene, "p_particle_hair_to_mesh_resolution", text="Resolution")
        row = particlehair_box.row()
        row.prop(mgtools_props_scene, "p_particle_hair_to_mesh_name", text="Name")
        particlehair_box.operator("mgtools.particle_hair_to_mesh", text="Particle Hair > Mesh",)


        ### toggle modifier -----------------------------------
        modifier_box = col.box()
        # label
        modifier_box.label(text="Modifier")

        # > to mesh
        row = modifier_box.row()
        row.prop(mgtools_props_scene, "p_modifier_toggle_name", text="Name")
        op = row.operator("mgtools.modifier_toggle", text="", icon="RESTRICT_VIEW_ON")
        op.modifier_toggle_name = mgtools_props_scene.p_modifier_toggle_name

        row = modifier_box.row()
        row.prop(mgtools_props_scene, "p_modifier_toggle_name_2", text="Name")
        op = row.operator("mgtools.modifier_toggle", text="", icon="RESTRICT_VIEW_ON")
        op.modifier_toggle_name = mgtools_props_scene.p_modifier_toggle_name_2

        row = modifier_box.row()
        row.prop(mgtools_props_scene, "p_modifier_toggle_name_3", text="Name")
        op = row.operator("mgtools.modifier_toggle", text="", icon="RESTRICT_VIEW_ON")
        op.modifier_toggle_name = mgtools_props_scene.p_modifier_toggle_name_3


        ### Custom attributes -----------------------------------
        attributes_box = col.box()
        # label
        attributes_box.label(text="Custom Attributes")

        # > to mesh
        row = attributes_box.row()
        row.prop(mgtools_props_scene, "p_attributes_vertex_positions_snapshot_name", text="Name")
        row = attributes_box.row()
        row.prop(mgtools_props_scene, "p_attributes_vertex_positions_snapshot_relative", text="Relative")
        row = attributes_box.row()
        op = row.operator("mgtools.vertices_to_attribute", text="Snapshot Vertex Positions")
        op.attribute_name = mgtools_props_scene.p_attributes_vertex_positions_snapshot_name
        op.relative = mgtools_props_scene.p_attributes_vertex_positions_snapshot_relative

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
        box.label(text="MGTO tools v0.6.27") # check also version in __init__
        box.label(text="by Till - rollin - Maginot")
        box.label(text="(C) 2024")

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
                row.label(text=str(round(weight_average,3)))
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
    
