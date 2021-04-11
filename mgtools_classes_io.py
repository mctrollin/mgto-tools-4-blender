import os
from math import radians
import bpy
from mathutils import Matrix # Vector, Euler, 
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_functions_io import MGTOOLS_functions_io

class MGTOOLS_io_exporter():

    # filename
    path = ""
    filename = ""
    filename_prefix_static = ""
    filename_prefix_skeletal = ""
    filename_prefix_animation = ""
    filepath = ""

    # axis
    axis_forward = '-Z'
    axis_up = 'Y'
    primary_bone_axis = 'Y'
    secondary_bone_axis = 'X'

    # pivot
    include_pivot_dummy = True
    include_pivot_dummy_if_required = False
    set_pivots_to_dummy = True
    export_from_origin = False
    alter_pivot_rotation = False
    pivot_rotation = (0,0,0)

    # mesh
    use_mesh_modifiers = True
    combine_meshes = False
    objectname_prefix = "to_export__"
    objectname_posfix = ""

    # armature
    armature_primary_rename = ''

    # animation settings
    animation_export_mode = ''
    animation_use_relative_frameranges = False
    animation_marker_start = ''
    animation_marker_end = ''

    # selection based options
    to_export_selection = []

    # collection based options
    to_export_collection = None
    pivot_dummy_prefix = ""


    def __init__(self, path, filename):

        # construct export file path
        self.path = bpy.path.abspath(path)
        self.filename = filename
        self.filepath = self.build_filepath(self.path, self.filename)


    def try_export_selection(self):
        print("Export (selection) to: " + self.filepath)

        if 0 >= len(self.to_export_selection):
            print(" > No export objects defined.")
            return

        # print selection content
        # for obj in to_export_selection:
        #     print(' > input_obj: ', obj.name)

        self.prepare_export(self.path)

        if False == MGTOOLS_functions_io.check_permissions(self.filepath):
            print(" > Permission denied.")
            return

        self.process_export(self.to_export_selection)

        print(" > Export (selection) finished for " + self.filepath)

    def try_export_collection(self):
        print("Export (collection) to: " + self.filepath)

        if None == self.to_export_collection:
            print(" > No export collection defined.")
            return

        # print collection content
        # for obj in self.to_export_collection.all_objects:
        #     print(' > input_obj: ', obj.name)

        if 0 >= len(self.to_export_collection.all_objects):
            print(" > Collection is empty.")
            return

        self.prepare_export(self.path)

        if False == MGTOOLS_functions_io.check_permissions(self.filepath):
            print(" > Permission denied.")
            return

        self.process_export(self.to_export_collection.all_objects.values())

        print(" > Export (collection) finished for " + self.filepath)

    def build_filepath(self, path, filename):
        return path + '\\' + filename + '.fbx'

    def prepare_export(self, path):
        # prepare path
        print ("Check and prepare directory: " + path)
        if not os.path.exists(path):
            os.mkdir(path)

    def call_fbx_export(self):
        
        # logging
        # for clone in to_export_clones:
        #     print("  > to_export_clone: {}".format(clone.name))
        print(" > export FBX:  filepath={}, axis_forward={}, axis_up={}, use_mesh_modifiers={},".format(
            self.filepath, self.axis_forward, self.axis_up, self.use_mesh_modifiers))

        # debug exit ----
        # return
        # ----------

        bpy.ops.export_scene.fbx(
            # os
            filepath=self.filepath,
            check_existing=False,
            # object
            axis_forward=self.axis_forward,
            axis_up=self.axis_up,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=False,
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            # mesh
            use_mesh_modifiers=self.use_mesh_modifiers,
            # material
            embed_textures=False,
            # rig
            add_leaf_bones=False,
            primary_bone_axis=self.primary_bone_axis,
            secondary_bone_axis=self.secondary_bone_axis,
            use_armature_deform_only=False,
            armature_nodetype='NULL',  # 'ROOT' gives good results if only exporting an armature
            # anim
            bake_anim=True,
            # Key All Bones, Force exporting at least one key of animation for all bones (needed with some target applications, like UE4)
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
        )

        ###### defaults: #########
        # filepath="",
        # check_existing=True,
        # filter_glob="*.fbx",
        # ui_tab='MAIN',
        # use_selection=False,
        # use_active_collection=False,
        # global_scale=1.0,
        # apply_unit_scale=True,
        # apply_scale_options='FBX_SCALE_NONE',
        # bake_space_transform=False,
        # object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
        # use_mesh_modifiers=True,
        # use_mesh_modifiers_render=True,
        # mesh_smooth_type='OFF',
        # use_mesh_edges=False,
        # use_tspace=False,
        # use_custom_props=False,
        # add_leaf_bones=True,
        # primary_bone_axis='Y',
        # secondary_bone_axis='X',
        # use_armature_deform_only=False,
        # armature_nodetype='NULL',
        # bake_anim=True,
        # bake_anim_use_all_bones=True,
        # bake_anim_use_nla_strips=True,
        # bake_anim_use_all_actions=True,
        # bake_anim_force_startend_keying=True,
        # bake_anim_step=1.0,
        # bake_anim_simplify_factor=1.0,
        # path_mode='AUTO',
        # embed_textures=False,
        # batch_mode='OFF',
        # use_batch_own_dir=True,
        # use_metadata=True,
        # axis_forward='-Z',
        # axis_up='Y'
        ########################

    def process_export(self, input_objects_raw):
        
        # copy incoming data into temporary var
        values = list(input_objects_raw)
        input_objects = []
        input_objects.extend(values)

        print ("Export now: {}".format(input_objects))

        # flags ----------------------------------
        # tmp: decide if we should create throw-away only-for-export clones or not
        # create_clones = False
        # if True == self.combine_meshes:
        #     create_clones = True
        create_clones = True
        # create a temporary collection and copy all input objects there
        create_temp_collection = False

        # checks ----------------------------------
        if None == input_objects:
            print(" > error: No objects defined for export")
            return

        # prepare ----------------------------------
        # create a temporary collection for exporting purposes
        tmp_export_collection = None
        if True == create_clones:
            if True == create_temp_collection:
                # create temporary collection (problem with unique names if we don't want ".001" etc. added to our exported objects)
                tmp_export_collection = MGTOOLS_functions_macros.duplicate_to_collection(input_objects, False)
                # make any containted collection instance real
                collection_objects = []
                for obj in tmp_export_collection.all_objects:
                    collection_objects.append(obj)
                for obj in collection_objects:
                    MGTOOLS_functions_macros.make_collection_instance_real(obj)
                # override to-process list with the new clones
                input_objects = tmp_export_collection.all_objects
            else:
                ## make collection instances real
                # collect collection instances
                input_collection_instances = []
                for obj in input_objects:
                    if None != obj.instance_collection:
                        input_collection_instances.append(obj)
                # create clones
                input_collection_instances_clones = []
                for ic in input_collection_instances:
                    MGTOOLS_functions_macros.select_objects(ic, True)
                    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
                    if 0 < len(bpy.context.selected_objects):
                        ic_clone = bpy.context.selected_objects[0]
                        input_collection_instances_clones.append(ic_clone)
                # make clones real
                to_remove_stuff = []
                for icc in input_collection_instances_clones:
                    to_remove_stuff.extend(MGTOOLS_functions_macros.make_collection_instance_real(icc))
                # add to to-process list
                input_objects.extend(to_remove_stuff)

        # filter objects into separate lists and try to find pivot dummy
        input_meshes = []
        input_helper = []
        input_armatures = []
        input_collectioninstances = []
        input_other = []
        input_pivot_dummy = None
        for obj in input_objects:
            # meshs
            if 'MESH' == obj.type:
                input_meshes.append(obj)
            # armatures
            elif 'ARMATURE' == obj.type:
                input_armatures.append(obj)
            # helper
            elif 'EMPTY' == obj.type:
                if 0 < len(self.pivot_dummy_prefix) and True == obj.name.startswith(self.pivot_dummy_prefix):
                    input_pivot_dummy = obj
                elif None != obj.instance_collection:
                    input_collectioninstances.append(obj)
                else:
                    input_helper.append(obj)
            # everything else
            else:
                input_other.append(obj)

            # process modifiers
            for mod in obj.modifiers:
                # armatures
                if 'ARMATURE' == mod.type:
                    # auto select armatures
                    armature_ref = mod.object
                    if False == (armature_ref in input_armatures):
                        input_armatures.append(armature_ref)


        to_export_meshes = input_meshes
        to_export_helper = input_helper
        to_export_armatures = input_armatures
        to_export_other = input_other
        to_export_pivot_dummy = input_pivot_dummy
        pivot_dummy_name = ""
        if None != to_export_pivot_dummy:
            pivot_dummy_name = to_export_pivot_dummy.name[len(self.pivot_dummy_prefix):]
        print(" > pivot dummy: {} name: {}".format(input_pivot_dummy, pivot_dummy_name))

        if 1 > len(to_export_meshes) and 1 > len(to_export_helper) and 1 > len(to_export_armatures) and 1 > len(to_export_other):
           print(" > nothing found to export for pivot: {}".format(input_pivot_dummy))
           return

        # option: created throw-away snapshots during export
        # pivot_dummy_clone = None
        input_meshes_clones = None
        if 0 < len(input_meshes) and True == create_clones:
            # create input_pivot_dummy throw-away snapshot
            # if None != input_pivot_dummy:
            #     pivot_dummy_clone = bpy.data.objects.new(self.prefix + input_pivot_dummy.name, None)
            #     # add to same collection
            #     input_pivot_dummy.users_collection[0].objects.link(pivot_dummy_clone)
            #     # apply same transforms
            #     pivot_dummy_clone.location = input_pivot_dummy.location
            #     pivot_dummy_clone.rotation_euler = input_pivot_dummy.rotation_euler
            #     pivot_dummy_clone.scale = input_pivot_dummy.scale
            #     # set as active pivot
            #     to_export_pivot_dummy = pivot_dummy_clone
        
            # create a throw-away snapshot of the object(s) we want to export
            print (" > creating to-export snapshots from {}".format(input_meshes))
            input_meshes_clones = MGTOOLS_functions_macros.make_snapshot_from(input_meshes, self.combine_meshes, self.objectname_prefix, self.objectname_posfix, False, None)
            to_export_meshes = input_meshes_clones
            print (" > snapshots created: {}".format(to_export_meshes))
            

            # do a view_layer refresh after creating clones
            bpy.context.view_layer.update()

            # post process clones -----

            # transfere modifier
            if True == self.combine_meshes:
                print(" > transfere (armature) modifier")
                MGTOOLS_functions_helper.transfere_modifier_armature(input_meshes, to_export_meshes)

            # adopt pivot from pivot-dummy
            if True == self.set_pivots_to_dummy and None != to_export_pivot_dummy:
                print(" > set pivot")
                MGTOOLS_functions_macros.set_pivot(to_export_meshes, to_export_pivot_dummy.location, to_export_pivot_dummy.rotation_euler, True)

            # misc
            for clone in to_export_meshes:
                # parent mesh snapshots to pivot snapshot
                # if None != pivot_dummy_clone:
                #     MGTOOLS_functions_helper.set_parent(clone, pivot_dummy_clone, True)
                # set clone names (if merged)
                if True == self.combine_meshes and 0 < len(pivot_dummy_name):
                    clone.name = pivot_dummy_name  # will add numbering automatically


        # cache original pivot-dummy transforms so we can revert it after export
        pivot_pos_cached = None
        pivot_rot_cached = None
        if None != to_export_pivot_dummy:
            pivot_pos_cached = to_export_pivot_dummy.location.copy()
            pivot_rot_cached = to_export_pivot_dummy.rotation_euler.copy()
            # print ("Cached transforms: {}, {}".format(pivot_pos_cached, pivot_rot_cached))


        # options ----------------------------------
        # option: move to origion
        if None != to_export_pivot_dummy:
            if True == self.export_from_origin:
                print (" > exporting from origin")
                to_export_pivot_dummy.location = (0,0,0)
            if True == self.alter_pivot_rotation:
                to_export_pivot_dummy.rotation_euler = tuple(radians(a) for a in self.pivot_rotation)
       

        # export ------------------------------------
        # select
        print("==> to_export_meshes: {}".format(to_export_meshes))
        print("==> to_export_helper: {}".format(to_export_helper))
        print("==> to_export_armatures: {}".format(to_export_armatures))
        print("==> to_export_other: {}".format(to_export_other))
        to_export_list = to_export_meshes + to_export_helper + to_export_armatures + to_export_other
        if True == self.include_pivot_dummy:
            include_pivot_dummy_final = True
            if True == self.include_pivot_dummy_if_required:
                include_pivot_dummy_final = 1 < len(to_export_list) 
            if True == include_pivot_dummy_final:
                to_export_list.append(to_export_pivot_dummy)
        MGTOOLS_functions_macros.select_objects(to_export_list, True)

        # update filepath
        used_filename_prefix = self.filename_prefix_static if 0 >= len(to_export_armatures) else self.filename_prefix_skeletal 
        self.filepath = self.build_filepath(self.path, used_filename_prefix + self.filename)

        # armature features
        armature_primary = None
        armature_primary_name_cached = ''
        if 0 < len(to_export_armatures):
            # we take the first armature in the list atm
            armature_primary = to_export_armatures[0]
            armature_primary_name_cached = armature_primary.name
            # rename armatures
            if '' != self.armature_primary_rename:
                armature_primary.name = self.armature_primary_rename

        # prepare anim related vars
        animation_strips_source = None

        # cache frame range
        cached_frame_start = bpy.context.scene.frame_start
        cached_frame_end = bpy.context.scene.frame_end

        if 'STRIPS' == self.animation_export_mode:
            # get object which holds animation strips information
            # Note: (here we are only interested on the frame ranges, not the actual animation data)
            animation_strips_source = to_export_armatures[0] if 0 < len(to_export_armatures) else None # for now we use the first armature
            # if None != actions_source_override: # TODO: if this is somehow necessary the property needs to be added (or moved from the obsolete animation batch export)
            #     animation_strips_source = actions_source_override

            # cache active action
            active_action_cached = animation_strips_source.animation_data.action if None != animation_strips_source else None

            strips = MGTOOLS_functions_helper.get_all_animstrips(animation_strips_source)
        
            for strip in strips:

                frame_start = strip.frame_start
                frame_end = strip.frame_end

                # relative animation range export 
                if True == self.animation_use_relative_frameranges:
                    # set active action of 'animation_strips_source' to strip's action
                    animation_strips_source.animation_data.action = strip.action
                    # modify start and end frame
                    frame_start = animation_strips_source.animation_data.action.frame_range[0]
                    frame_end = animation_strips_source.animation_data.action.frame_range[1]

                # set scene frame range
                bpy.context.scene.frame_start = frame_start
                bpy.context.scene.frame_end = frame_end

                print(" > anim export: {} / {}, frame_abs:({} - {}), frame_rel:({} - {})".format(
                    strip.name, strip.action.name, strip.frame_start, strip.frame_end, frame_start, frame_end))

                # update filename for animation export
                self.filepath = self.build_filepath(self.path, self.filename_prefix_animation + self.filename + strip.action.name)

                self.call_fbx_export()

        elif 'MARKERS' == self.animation_export_mode:
            
            marker_idx = -1
            animation_name = ''
            
            timeline_markers_sorted = bpy.context.scene.timeline_markers.values()
            timeline_markers_sorted.sort(key=lambda x: x.frame, reverse=False)

            for marker in timeline_markers_sorted:
                marker_idx += 1

                # start marker of an animation
                is_start = 0 < len(self.animation_marker_start) and 0 <= marker.name.find(self.animation_marker_start)
                # end marker of an animation
                is_end = 0 < len(self.animation_marker_end) and 0 <= marker.name.find(self.animation_marker_end)
                # very last marker in the scene
                is_last = len(timeline_markers_sorted) - 1 == marker_idx

                print(" > marker {}: {}, is_start:{}, is_end:{}, is_last:{}, current anim:{}".format(marker_idx, marker.name, is_start, is_end, is_last, animation_name))

                # found start-marker
                if True == is_start:
                    # set scene frame start
                    bpy.context.scene.frame_start = marker.frame

                    animation_name = marker.name.replace(self.animation_marker_start, '')

                # found end-marker (terminator) or if last marker
                elif True == is_end:
                    # set scene frame end
                    bpy.context.scene.frame_end = marker.frame
                
                if True == is_last:
                    # set scene frame end
                    bpy.context.scene.frame_end = cached_frame_end if cached_frame_end > bpy.context.scene.frame_start else marker.frame

                if True == is_end or True == is_last and 0 < len(animation_name):
                    print(" > export now {}".format(animation_name))

                    # update filename for animation export
                    self.filepath = self.build_filepath(self.path, self.filename_prefix_animation + self.filename + animation_name)

                    self.call_fbx_export()

                    # important: reset name
                    animation_name = ''

        else:
            self.call_fbx_export()


        # cleanup ------------------------------------

        # revert armature name
        if None != armature_primary:
            armature_primary.name = armature_primary_name_cached

        # revert active action
        if None != animation_strips_source:
            animation_strips_source.animation_data.action = active_action_cached

        # revert scene frame range
        bpy.context.scene.frame_start = cached_frame_start
        bpy.context.scene.frame_end = cached_frame_end

        # revert pivot transforms
        if None != to_export_pivot_dummy:
            print(" > reverting pivot transforms")
            # print ("Cached transforms: {}, {}".format(pivot_pos_cached, pivot_rot_cached))
            to_export_pivot_dummy.location = pivot_pos_cached
            to_export_pivot_dummy.rotation_euler = pivot_rot_cached

        # delete clones after export
        print(" > removing temporary export files")

        # if None != pivot_dummy_clone:
        #     bpy.data.objects.remove(pivot_dummy_clone)

        if None != input_meshes_clones:
            for clone in input_meshes_clones:
                bpy.data.objects.remove(clone)

        if None != tmp_export_collection:
            for clone in tmp_export_collection.objects:
                bpy.data.objects.remove(clone)
            bpy.data.collections.remove(tmp_export_collection)

        if None != to_remove_stuff:
            for clone in to_remove_stuff:
                MGTOOLS_functions_helper.remove_recursive(clone)  # bpy.data.objects.remove(clone)

    @classmethod
    def quick_export_anim(self, path, filename, frame_start, frame_end):

        self.prepare_export(self, path)
        filepath = self.build_filepath(self, path, filename)

        if False == MGTOOLS_functions_io.check_permissions(filepath):
            print(" > Permission denied.")
            return

        # cache frame range
        cached_frame_start = bpy.context.scene.frame_start
        cached_frame_end = bpy.context.scene.frame_end

        # set scene frame range
        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end

        # export
        print(" > export FBX:  filepath={}, axis_forward={}, axis_up={}, use_mesh_modifiers={},".format(
            filepath, self.axis_forward, self.axis_up, self.use_mesh_modifiers))

        bpy.ops.export_scene.fbx(
            # os
            filepath=filepath,
            check_existing=False,
            # object
            axis_forward=self.axis_forward,
            axis_up=self.axis_up,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=False,
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            # mesh
            use_mesh_modifiers=self.use_mesh_modifiers,
            # material
            embed_textures=False,
            # rig
            add_leaf_bones=False,
            primary_bone_axis=self.primary_bone_axis,
            secondary_bone_axis=self.secondary_bone_axis,
            use_armature_deform_only=False,
            armature_nodetype='NULL',  # 'ROOT' gives good results if only exporting an armature
            # anim
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
        )

        # revert scene frame range
        bpy.context.scene.frame_start = cached_frame_start
        bpy.context.scene.frame_end = cached_frame_end
