import os
import copy
import subprocess
import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_functions_io import MGTOOLS_functions_io
from . mgtools_functions_gamedev import MGTOOLS_functions_gamedev
from . mgtools_classes_io import MGTOOLS_io_exporter

class MGTOOLS_OT_export_collections(Operator):
    bl_idname = "mgtools.io_export_collections"
    bl_label = "Export Collections"
    bl_description = ""

    def execute(self, context):
        # read properties -----------------------------------
        mgtools_props_scene = bpy.context.scene.mgtools
        
        # backward compatibility fix TODO: remove this later
        if 'SM_' == mgtools_props_scene.p_io_export_filename_prefix: 
            mgtools_props_scene.p_io_export_filename_prefix = ''
            mgtools_props_scene.p_io_export_filename_prefix_static = 'SM_'
        ####################################################
        filename_include_blendfilename = mgtools_props_scene.p_io_export_filename_include_blendfilename
        filename_ignore_collection_dot_prefix = mgtools_props_scene.p_io_export_filename_ignore_collection_dot_prefix

        export_folder = mgtools_props_scene.p_io_export_folder_collections

        filter_prefix_collection = mgtools_props_scene.p_io_export_prefix_filter_collection

        # loop through all collections -----------------------------------
        for collection in bpy.data.collections:
            print("Processing collection: {} ".format(collection.name))
            
            # filter only collections which should be exported
            if False == collection.name.startswith(filter_prefix_collection) or len(collection.name) < len(filter_prefix_collection):
                print (" > Skipping: not tagged for export with '{}'".format(filter_prefix_collection))
                continue

            layercollection = MGTOOLS_functions_helper.get_layercollection(collection)
            if None == layercollection:
                print (" > Skipping: can't find related LayerCollection")
                continue
            if True == layercollection.exclude:
                print (" > Skipping: collection is excluded from ViewLayers")
                continue
            if True == layercollection.hide_viewport:
                print (" > Skipping: collection is hidden in ViewLayer viewport")
                continue
            if True == layercollection.collection.hide_select:
                print (" > Skipping: collection is not selectable")
                continue
            
            # prepare -----------------------------------

            # prepare filename
            filename = collection.name[len(filter_prefix_collection):]
            if True == filename_ignore_collection_dot_prefix:
                filename = filename.rsplit('.', 1)[0]
            if True == filename_include_blendfilename:
                if 0 < len(filename):
                    filename = "_" + filename
                filename = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0] + filename
            # filename = filename_prefix + filename # this is now done by the exporter class itself

            # create new exporter instance and set it up -----------------------------------
            exporter = MGTOOLS_io_exporter(export_folder, filename)
            # filename
            exporter.filename_prefix = mgtools_props_scene.p_io_export_filename_prefix
            exporter.filename_prefix_static = mgtools_props_scene.p_io_export_filename_prefix_static
            exporter.filename_prefix_skeletal = mgtools_props_scene.p_io_export_filename_prefix_skeletal
            exporter.filename_prefix_animation = mgtools_props_scene.p_io_export_filename_prefix_animation
            exporter.filename_postfix = mgtools_props_scene.p_io_export_filename_postfix
            # axis
            exporter.axis_forward = mgtools_props_scene.p_io_export_axis_forward
            exporter.axis_up = mgtools_props_scene.p_io_export_axis_up
            exporter.primary_bone_axis = mgtools_props_scene.p_io_export_primary_bone_axis
            exporter.secondary_bone_axis = mgtools_props_scene.p_io_export_secondary_bone_axis
            # scale
            exporter.scale_apply_options = mgtools_props_scene.p_io_export_scale_apply_options
            exporter.use_space_transform = mgtools_props_scene.p_io_export_use_space_transform
            exporter.scale = mgtools_props_scene.p_io_export_scale
            exporter.apply_unit_scale = mgtools_props_scene.p_io_export_apply_unit_scale
            # pivot
            exporter.pivot_dummy_prefix = mgtools_props_scene.p_io_export_prefix_filter_pivot
            exporter.include_pivot_dummy = mgtools_props_scene.p_io_export_include_pivot_dummy
            exporter.include_pivot_dummy_if_required = mgtools_props_scene.p_io_export_include_pivot_dummy_if_required
            exporter.set_pivots_to_dummy = mgtools_props_scene.p_io_export_set_pivots_to_dummy
            exporter.pivot_reset_location = mgtools_props_scene.p_io_export_pivot_reset_location
            exporter.pivot_reset_rotation = mgtools_props_scene.p_io_export_pivot_reset_rotation
            exporter.pivot_reset_scale = mgtools_props_scene.p_io_export_pivot_reset_scale
            exporter.pivot_rotation = mgtools_props_scene.p_io_export_rotation
            exporter.export_pivot_dummy_disable_constraints = mgtools_props_scene.p_io_export_pivot_dummy_disable_constraints
            # helper
            exporter.export_helper_strip_dotnumbers = mgtools_props_scene.p_io_export_helper_strip_dotnumbers
            # mesh
            #exporter.use_mesh_modifiers = mgtools_props_scene.p_io_export_use_mesh_modifiers # the exporter process currently requires to always apply them
            exporter.use_mesh_modifiers_armature = mgtools_props_scene.p_io_export_use_mesh_modifiers_armature
            exporter.mesh_smooth_type = mgtools_props_scene.p_io_export_mesh_smooth_type
            exporter.combine_meshes = mgtools_props_scene.p_io_export_combine_meshes
            exporter.clone_meshes_filter = mgtools_props_scene.p_io_export_clone_meshes_filter
            exporter.combine_meshes_filter = mgtools_props_scene.p_io_export_combine_meshes_filter
            exporter.objectname_prefix = mgtools_props_scene.p_io_export_objectname_prefix
            exporter.objectname_postfix = mgtools_props_scene.p_io_export_objectname_postfix
            exporter.vgroups_rename = mgtools_props_scene.p_io_export_vgroups_rename
            exporter.vgroups_rename_mapping_file_path = mgtools_props_scene.p_io_export_vgroups_rename_mapping_file_path
            exporter.vgroups_rename_invert_mapping = mgtools_props_scene.p_io_export_vgroups_rename_mapping_inverse
            exporter.armature_replacement = mgtools_props_scene.p_io_export_armature_replacement
            exporter.weights_limit = mgtools_props_scene.p_io_export_weights_limit
            #material
            exporter.material_override = mgtools_props_scene.p_io_export_material_override
            # armature
            exporter.armature_primary_rename = mgtools_props_scene.p_io_export_armature_rename
            # anim
            exporter.animation_export_mode = mgtools_props_scene.p_io_export_animation_mode
            exporter.export_frame = mgtools_props_scene.p_io_export_frame
            exporter.animation_use_relative_frameranges = mgtools_props_scene.p_io_export_animation_use_relative_frameranges
            exporter.animation_marker_start = mgtools_props_scene.p_io_export_animation_marker_start
            exporter.animation_marker_end = mgtools_props_scene.p_io_export_animation_marker_end
            exporter.bake_anim_simplify_factor = mgtools_props_scene.p_io_export_animation_bake_anim_simplify_factor
            
            # start the export -----------------------------------
            exporter.to_export_collection = collection
            exporter.try_export_collection()

        return{'FINISHED'}

class MGTOOLS_OT_export_selection(Operator):
    bl_idname = "mgtools.io_export_selection"
    bl_label = "Export Selection"
    bl_description = ""

    def execute(self, context):
        # read properties -----------------------------------
        mgtools_props_scene = bpy.context.scene.mgtools

        # export_folder = mgtools_props_scene.p_io_export_folder_collections

        # prepare -----------------------------------

        # choose objects to export
        objects = bpy.context.selected_objects

        # prepare filename
        export_filepath = mgtools_props_scene.p_io_export_filepath
        export_folder = os.path.dirname(export_filepath)
        filename = os.path.splitext(os.path.basename(export_filepath))[0]

        # create new exporter instance and set it up -----------------------------------
        exporter = MGTOOLS_io_exporter(export_folder, filename)
        exporter.filename_prefix = '' # this is skipped for a manual export
        exporter.filename_prefix_static = '' # this is skipped for a manual export
        exporter.filename_prefix_skeletal = '' # this is skipped for a manual export
        exporter.filename_prefix_animation = mgtools_props_scene.p_io_export_filename_prefix_animation
        exporter.filename_postfix = '' # this is skipped for a manual export
        # axis
        exporter.axis_forward = mgtools_props_scene.p_io_export_axis_forward
        exporter.axis_up = mgtools_props_scene.p_io_export_axis_up
        exporter.primary_bone_axis = mgtools_props_scene.p_io_export_primary_bone_axis
        exporter.secondary_bone_axis = mgtools_props_scene.p_io_export_secondary_bone_axis
        # scale
        exporter.scale_apply_options = mgtools_props_scene.p_io_export_scale_apply_options
        exporter.use_space_transform = mgtools_props_scene.p_io_export_use_space_transform
        exporter.scale = mgtools_props_scene.p_io_export_scale
        exporter.apply_unit_scale = mgtools_props_scene.p_io_export_apply_unit_scale
        # pivot
        exporter.pivot_dummy_prefix = mgtools_props_scene.p_io_export_prefix_filter_pivot
        exporter.include_pivot_dummy = mgtools_props_scene.p_io_export_include_pivot_dummy
        exporter.include_pivot_dummy_if_required = mgtools_props_scene.p_io_export_include_pivot_dummy_if_required
        exporter.set_pivots_to_dummy = mgtools_props_scene.p_io_export_set_pivots_to_dummy
        exporter.pivot_reset_location = mgtools_props_scene.p_io_export_pivot_reset_location
        exporter.pivot_reset_rotation = mgtools_props_scene.p_io_export_pivot_reset_rotation
        exporter.pivot_reset_scale = mgtools_props_scene.p_io_export_pivot_reset_scale
        exporter.pivot_rotation = mgtools_props_scene.p_io_export_rotation
        exporter.export_pivot_dummy_disable_constraints = mgtools_props_scene.p_io_export_pivot_dummy_disable_constraints
        # helper
        exporter.export_helper_strip_dotnumbers = mgtools_props_scene.p_io_export_helper_strip_dotnumbers
        # mesh
        #exporter.use_mesh_modifiers = mgtools_props_scene.p_io_export_use_mesh_modifiers # the exporter process currently requires to always apply them
        exporter.use_mesh_modifiers_armature = mgtools_props_scene.p_io_export_use_mesh_modifiers_armature
        exporter.mesh_smooth_type = mgtools_props_scene.p_io_export_mesh_smooth_type
        exporter.combine_meshes = mgtools_props_scene.p_io_export_combine_meshes
        exporter.clone_meshes_filter = mgtools_props_scene.p_io_export_clone_meshes_filter
        exporter.combine_meshes_filter = mgtools_props_scene.p_io_export_combine_meshes_filter
        exporter.objectname_prefix = mgtools_props_scene.p_io_export_objectname_prefix
        exporter.objectname_postfix = mgtools_props_scene.p_io_export_objectname_postfix
        exporter.vgroups_rename = mgtools_props_scene.p_io_export_vgroups_rename
        exporter.vgroups_rename_mapping_file_path = mgtools_props_scene.p_io_export_vgroups_rename_mapping_file_path
        exporter.vgroups_rename_invert_mapping = mgtools_props_scene.p_io_export_vgroups_rename_mapping_inverse
        exporter.armature_replacement = mgtools_props_scene.p_io_export_armature_replacement
        exporter.weights_limit = mgtools_props_scene.p_io_export_weights_limit
        #material
        exporter.material_override = mgtools_props_scene.p_io_export_material_override
        # armature
        exporter.armature_primary_rename = mgtools_props_scene.p_io_export_armature_rename
        # anim
        exporter.animation_export_mode = mgtools_props_scene.p_io_export_animation_mode
        exporter.export_frame = mgtools_props_scene.p_io_export_frame
        exporter.animation_use_relative_frameranges = mgtools_props_scene.p_io_export_animation_use_relative_frameranges
        exporter.animation_marker_start = mgtools_props_scene.p_io_export_animation_marker_start
        exporter.animation_marker_end = mgtools_props_scene.p_io_export_animation_marker_end
        exporter.bake_anim_simplify_factor = mgtools_props_scene.p_io_export_animation_bake_anim_simplify_factor

        # start the export -----------------------------------
        exporter.to_export_selection = objects
        exporter.try_export_selection()

        return{'FINISHED'}

# obsolete as we now export animations directly as part of the collection / selection export 
class MGTOOLS_OT_export_animations(Operator):
    bl_idname = "mgtools.io_export_animations"
    bl_label = "Export Animations"
    bl_description = ""

    def execute(self, context):
        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools

        export_folder = mgtools_props_scene.p_io_export_animation_folder
        actions_source_override = mgtools_props_scene.p_io_export_animation_actions_reference_override
        use_relative_frameranges = mgtools_props_scene.p_io_export_animation_use_relative_frameranges
        file_prefix = mgtools_props_scene.p_io_export_filename_prefix_animation

        # choose object to export (make sure there is one selected)
        # objects = bpy.context.selected_objects
        if None == bpy.context.view_layer.objects.active:
            return{'CANCELLED'}

        # get object which holds animation strips information 
        # Note: (here we are only interested on the frame ranges, not the actual animation data)
        strips_source = bpy.context.view_layer.objects.active #objects[0]
        if None != actions_source_override:
            strips_source = actions_source_override

        # check animation data
        if None == strips_source.animation_data:
            return{'CANCELLED'}

        # cache active action
        active_action_cached = strips_source.animation_data.action

        strips = MGTOOLS_functions_helper.get_all_animstrips(strips_source)
        print ("To-Export NLA-strips:")
        for strip in strips:
            # strip.action.name = "a" + strip.name[1:] # change animation action name
            frame_start = strip.frame_start
            frame_end = strip.frame_end

            # relative animation range export --------------------------
            if True == use_relative_frameranges:
                # set active action of 'strips_source' to strip's action
                strips_source.animation_data.action = strip.action
                # modify start and end frame
                frame_start = strips_source.animation_data.action.frame_range[0]
                frame_end = strips_source.animation_data.action.frame_range[1]

            print ("  - {} / {}, frame_abs:({} - {}), frame_rel:({} - {})".format(strip.name, strip.action.name, strip.frame_start, strip.frame_end, frame_start, frame_end))
            
            filename = file_prefix + strip.action.name
            export_folder = bpy.path.abspath(export_folder)
            MGTOOLS_io_exporter.quick_export_anim(export_folder, filename, frame_start, frame_end)

        # revert active action
        strips_source.animation_data.action = active_action_cached

        return{'FINISHED'}

class MGTOOLS_OT_export_hitboxes(Operator):
    bl_idname = "mgtools.io_export_hitboxes"
    bl_label = "Export Hitboxes"
    bl_description = ""

    def execute(self, context):
        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools

        export_folder = mgtools_props_scene.p_io_export_folder_collections
        filter_prefix_collection_hitboxes = mgtools_props_scene.p_io_export_prefix_filter_collection_hitboxes

        # loop through all collections
        for collection in bpy.data.collections:
            print("Processing collection: " + collection.name)

            # filter only collections which should be exported
            if False == collection.name.startswith(filter_prefix_collection_hitboxes) or len(collection.name) <= len(filter_prefix_collection_hitboxes):
                # print (" > Skipping: not tagged for export with '{}'".format(filter_prefix_collection_hitboxes))
                continue

            # prepare filename
            filename = collection.name[len(filter_prefix_collection_hitboxes):]

            # get hitboxes
            hitboxes_objects = collection.all_objects

            # prepare formated export string
            hitboxes_string = MGTOOLS_functions_gamedev.get_hitboxes_string(hitboxes_objects)

            # print ("hitboxes_string: {}".format(hitboxes_string))

            if 0 < len(hitboxes_string):
                # add wrapping tags
                hitboxes_string = "<collider>\n" + hitboxes_string + "</collider>"
                # write data to file
                MGTOOLS_functions_io.export_textfile(export_folder, filename, 'txt', hitboxes_string)
            else:
                print ("No data to write")
        
        return{'FINISHED'}



class MGTOOLS_OT_open_collections_export_folder(Operator):
    bl_idname = "mgtools.io_open_collections_export_folder"
    bl_label = "Open Export Folder"
    bl_description = ""

    def execute(self, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        path = mgtools_props_scene.p_io_export_folder_collections
        path = bpy.path.abspath(path)
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}

class MGTOOLS_OT_open_selection_export_folder(Operator):
    bl_idname = "mgtools.io_open_selection_export_folder"
    bl_label = "Open Export Folder"
    bl_description = ""

    def execute(self, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        path = os.path.dirname(mgtools_props_scene.p_io_export_filepath)
        path = bpy.path.abspath(path)
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}

class MGTOOLS_OT_open_animations_export_folder(Operator):
    bl_idname = "mgtools.io_open_animations_export_folder"
    bl_label = "Open Export Folder"
    bl_description = ""

    def execute(self, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        path = mgtools_props_scene.p_io_export_animation_folder
        path = bpy.path.abspath(path)
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}