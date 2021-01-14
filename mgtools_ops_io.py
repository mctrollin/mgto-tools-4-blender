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
        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools
        
        export_folder = mgtools_props_scene.p_io_export_folder_collections
        export_from_origin = mgtools_props_scene.p_io_export_from_origin
        alter_rotation = mgtools_props_scene.p_io_export_alter_rotation
        pivot_rotation = mgtools_props_scene.p_io_export_rotation
        combine_meshes = mgtools_props_scene.p_io_export_merge
        axis_forward = mgtools_props_scene.p_io_export_axis_forward
        axis_up = mgtools_props_scene.p_io_export_axis_up
        use_mesh_modifiers = mgtools_props_scene.p_io_export_use_mesh_modifiers
        export_name_prefix = mgtools_props_scene.p_io_export_name_prefix
        export_name_posfix = mgtools_props_scene.p_io_export_name_posfix
        filter_prefix_collection = mgtools_props_scene.p_io_export_prefix_filter_collection
        filter_prefix_pivot = mgtools_props_scene.p_io_export_prefix_filter_pivot
        filename_prefix = mgtools_props_scene.p_io_export_filename_prefix
        filename_include_blendfilename = mgtools_props_scene.p_io_export_filename_include_blendfilename
        include_pivot_dummy = mgtools_props_scene.p_io_export_include_pivot_dummy
        include_pivot_dummy_if_required = mgtools_props_scene.p_io_export_include_pivot_dummy_if_required
        set_pivots_to_dummy = mgtools_props_scene.p_io_export_set_pivots_to_dummy

        # loop through all collections
        for collection in bpy.data.collections:
            print("Processing collection: " + collection.name)
            
            # filter only collections which should be exported
            if False == collection.name.startswith(filter_prefix_collection) or len(collection.name) <= len(filter_prefix_collection):
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

            # prepare filename
            filename = collection.name[len(filter_prefix_collection):]
            if True == filename_include_blendfilename:
                filename = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0] + "_" + filename
            filename = filename_prefix + filename

            # create new exporter instance and set it up
            exporter = MGTOOLS_io_exporter(export_folder, filename)
            exporter.axis_forward = axis_forward
            exporter.axis_up = axis_up
            exporter.use_mesh_modifiers = use_mesh_modifiers
            exporter.export_from_origin = export_from_origin
            exporter.alter_pivot_rotation = alter_rotation
            exporter.pivot_rotation = pivot_rotation
            exporter.combine_meshes = combine_meshes
            exporter.to_export_collection = collection
            exporter.prefix = export_name_prefix
            exporter.posfix = export_name_posfix
            exporter.pivot_dummy_prefix = filter_prefix_pivot
            exporter.include_pivot_dummy = include_pivot_dummy
            exporter.include_pivot_dummy_if_required = include_pivot_dummy_if_required
            exporter.set_pivots_to_dummy = set_pivots_to_dummy

            # start the export
            exporter.try_export_collection()

        return{'FINISHED'}

class MGTOOLS_OT_export_selection(Operator):
    bl_idname = "mgtools.io_export_selection"
    bl_label = "Export Selection"
    bl_description = ""

    def execute(self, context):
        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools

        export_filepath = mgtools_props_scene.p_io_export_filepath
        export_folder = os.path.dirname(export_filepath)
        filename = os.path.splitext(os.path.basename(export_filepath))[0]
        export_from_origin = mgtools_props_scene.p_io_export_from_origin
        alter_rotation = mgtools_props_scene.p_io_export_alter_rotation
        pivot_rotation = mgtools_props_scene.p_io_export_rotation
        combine_meshes = mgtools_props_scene.p_io_export_merge
        filter_prefix_pivot = mgtools_props_scene.p_io_export_prefix_filter_pivot

        # choose objects to export
        objects = bpy.context.selected_objects

        # create new exporter instance and set it up
        exporter = MGTOOLS_io_exporter(export_folder, filename)
        exporter.to_export_selection = objects
        exporter.export_from_origin = export_from_origin
        exporter.alter_pivot_rotation = alter_rotation
        exporter.pivot_rotation = pivot_rotation
        exporter.combine_meshes = combine_meshes
        exporter.pivot_dummy_prefix = filter_prefix_pivot

        # start the export
        exporter.try_export_selection()

        return{'FINISHED'}

class MGTOOLS_OT_export_animations(Operator):
    bl_idname = "mgtools.io_export_animations"
    bl_label = "Export Animations"
    bl_description = ""

    def execute(self, context):
        # read properties
        mgtools_props_scene = bpy.context.scene.mgtools

        export_folder = mgtools_props_scene.p_io_export_folder_animations
        actions_source_override = mgtools_props_scene.p_io_export_actions_reference_override
        use_relative_frameranges = mgtools_props_scene.p_io_export_use_relative_frameranges
        file_prefix = mgtools_props_scene.p_io_export_animation_file_prefix

        # choose objects to export
        # objects = bpy.context.selected_objects

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
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}

class MGTOOLS_OT_open_selection_export_folder(Operator):
    bl_idname = "mgtools.io_open_selection_export_folder"
    bl_label = "Open Export Folder"
    bl_description = ""

    def execute(self, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        path = os.path.dirname(mgtools_props_scene.p_io_export_filepath)
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}

class MGTOOLS_OT_open_animations_export_folder(Operator):
    bl_idname = "mgtools.io_open_animations_export_folder"
    bl_label = "Open Export Folder"
    bl_description = ""

    def execute(self, context):
        mgtools_props_scene = bpy.context.scene.mgtools
        path = mgtools_props_scene.p_io_export_folder_animations
        subprocess.Popen('explorer {path}'.format(path = path))
        return {'FINISHED'}