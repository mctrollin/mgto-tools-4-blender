import os
from math import radians
import bpy
from mathutils import Matrix # Vector, Euler, 
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_functions_io import MGTOOLS_functions_io
from . mgtools_functions_rename import MGTOOLS_functions_rename

class MGTOOLS_io_exporter():

    # filename
    path = ""
    filename = ""
    filename_prefix = ""
    filename_prefix_static = ""
    filename_prefix_skeletal = ""
    filename_prefix_animation = ""
    filename_postfix = ""
    filepath = ""

    # axis
    axis_forward = '-Z'
    axis_up = 'Y'
    primary_bone_axis = 'Y'
    secondary_bone_axis = 'X'

    # scale
    scale_apply_options = 'FBX_SCALE_ALL'
    use_space_transform = True
    scale = 1
    apply_unit_scale = True

    # pivot
    pivot_dummy_prefix = ""
    include_pivot_dummy = True
    include_pivot_dummy_if_required = False
    set_pivots_to_dummy = True
    pivot_reset_location = False
    pivot_reset_rotation = False
    pivot_reset_scale = False
    pivot_rotation = (0,0,0)
    pivot_dummy_disable_constraints = False

    # helper
    helper_strip_dotnumbers = False

    # mesh
    use_mesh_modifiers = False # used by fbx exporter
    use_mesh_modifier_armature = False # usually we don't want to apply the armature
    combine_meshes = False
    combine_meshes_filter = ""
    objectname_prefix = "to_export__"
    objectname_postfix = ""
    vgroups_rename = False
    vgroups_rename_mapping_file_path = ""
    vgroups_rename_invert_mapping = False
    armature_replacement = None

    # armature
    armature_primary_rename = ''

    # animation settings
    animation_export_mode = ''
    export_frame = 0
    animation_use_relative_frameranges = False
    animation_marker_start = ''
    animation_marker_end = ''
    bake_anim_simplify_factor=0.0

    # selection based options
    to_export_selection = []

    # collection based options
    to_export_collection = None


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

        # moved this right in front of the actual fbx export as we like to continue exporting e.g. animations even if one is locked
        # if False == MGTOOLS_functions_io.check_permissions(self.filepath):
        #     print(" > Permission denied.")
        #     return

        self.process_export(self.to_export_selection)

        print(" > Export (selection) finished.")

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

        # moved this right in front of the actual fbx export as we like to continue exporting e.g. animations even if one is locked
        # if False == MGTOOLS_functions_io.check_permissions(self.filepath):
        #     print(" > Permission denied.")
        #     return

        self.process_export(self.to_export_collection.all_objects.values())

        print(" > Export (collection) finished.")

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
        print(" > exporting FBX:  filepath={}".format(self.filepath))

        if False == MGTOOLS_functions_io.check_permissions(self.filepath):
            print(" > Permission denied! Sorry, I'm not able to write to this file. :(")
            return

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
            global_scale=self.scale,
            apply_unit_scale=self.apply_unit_scale,
            apply_scale_options=self.scale_apply_options,
            use_space_transform=self.use_space_transform,
            bake_space_transform=False,
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            # mesh
            use_mesh_modifiers=self.use_mesh_modifiers,
            mesh_smooth_type=self.mesh_smooth_type,
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
            bake_anim_simplify_factor=self.bake_anim_simplify_factor,
        )

        print(" > exporting FBX done")

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
        
        # copy incoming data into working list
        input_objects = []
        input_objects.extend(list(input_objects_raw))
        print ("Export now: {}".format(input_objects))
        if None == input_objects:
            print(" > Error: No objects defined for export!")
            return

        # flags ----------------------------------
        # tmp: decide if we should create throw-away only-for-export clones or not
        # create_clones = False
        # if True == self.combine_meshes:
        #     create_clones = True
        create_clones = True
        # create a temporary collection and copy all input objects there
        create_temp_collection = False

        # prepare ----------------------------------


        # Cache edit mode and activate object mode
        active_mode_cached = bpy.context.object.mode if None != bpy.context.object else ''
        if '' != active_mode_cached:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Cache selection
        active_object_cached = bpy.context.view_layer.objects.active
        selected_objects_cached = bpy.context.selected_objects

        # if None == active_object_cached:
        #     print(" > Error: No active objects defined for export!")
        #     return

        # create a temporary collection for exporting purposes
        tmp_export_collection = None
        if True == create_clones:
            # create a temporary to-export collection
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
            # find, clone and make-real any collection instances
            else:
                # get collection instances
                input_collection_instances = []
                for obj in input_objects:
                    if None != obj.instance_collection:
                        input_collection_instances.append(obj)
                # create clones of these instances
                input_collection_instances_clones = []
                for ic in input_collection_instances:
                    MGTOOLS_functions_macros.select_objects(ic, True)
                    bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
                    if 0 < len(bpy.context.selected_objects):
                        ic_clone = bpy.context.selected_objects[0]
                        input_collection_instances_clones.append(ic_clone)
                # make clones real
                collection_instances_content_clones = []
                for icc in input_collection_instances_clones:
                    collection_instances_content_clones.extend(MGTOOLS_functions_macros.make_collection_instance_real(icc))
                # add to to-process list
                input_objects.extend(collection_instances_content_clones)

       
        # -------------------
        input_meshes = []
        input_helper = []
        input_armatures = []
        input_collectioninstances = []
        input_other = []
        input_pivot_dummy = None

        # pre-set armatures
        if None != self.armature_replacement and False == (self.armature_replacement in input_armatures):
                if not self.armature_replacement.visible_get():
                    print(" > Warning: armature is hidden and therefore can't be exported: {} ".format(self.armature_replacement))
                else:
                    input_armatures.append(self.armature_replacement)

        # filter objects into separate lists and try to find pivot dummy
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
                    # disable the modifier - when we later snapshot the mesh it gets not applied
                    if False == self.use_mesh_modifier_armature:
                        mod.is_active = False
                    # skip if an armature replacement is set (not perfect but the least complex solution atm)
                    if None == self.armature_replacement:
                        # get armature ref
                        armature_ref = mod.object
                        # auto select armatures (if not hidden)
                        if None != armature_ref and False == (armature_ref in input_armatures):
                            if not armature_ref.visible_get():
                                print(" > Warning: armature is hidden and therefore can't be exported: {} ".format(armature_ref))
                            else:
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
        input_meshes_clones = []
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

            transfer_modifier = self.combine_meshes

            # create a throw-away snapshot of the object(s) we want to export

            # apply filter -----
            input_meshes_to_snapshot = []
            input_meshes_not_to_snapshot = []
            combine_meshes_filter_list = self.combine_meshes_filter.split(",")
            if 0 < len(combine_meshes_filter_list):
                for input_mesh in input_meshes:
                    # check exclude-by-name filter
                    input_mesh_processed = False
                    for merge_filter_name in combine_meshes_filter_list:
                        if 0 < len(merge_filter_name) and merge_filter_name in input_mesh.name:     
                            input_meshes_not_to_snapshot.append(input_mesh)
                            input_mesh_processed = True                    
                            break
                    if False == input_mesh_processed:
                        input_meshes_to_snapshot.append(input_mesh)

            print (" > creating to-export snapshots from: {} excluding: {}".format(input_meshes_to_snapshot, input_meshes_not_to_snapshot))
            
            # create snapshot(s) -----
            if True == self.combine_meshes:
                input_meshes_clones = MGTOOLS_functions_macros.make_snapshot_from(
                    source_objects_raw=input_meshes_to_snapshot,
                    merge=self.combine_meshes, 
                    prefix=self.objectname_prefix, 
                    postfix=self.objectname_postfix, 
                    select_clones=False, 
                    type_filter=None)
            else:
                for input_mesh_to_snapshot in input_meshes_to_snapshot:
                    input_mesh_snapshot = MGTOOLS_functions_macros.make_snapshot_from(
                        source_objects_raw=[input_mesh_to_snapshot], 
                        merge=True, 
                        prefix=self.objectname_prefix, 
                        postfix=self.objectname_postfix, 
                        select_clones=False, 
                        type_filter=None)
                    input_meshes_clones += input_mesh_snapshot
                transfer_modifier = True # necessary as the merge command applies them all
            
            # set clone names (if merged it should be only one object)
            if True == self.combine_meshes and 0 < len(input_meshes_clones):
                for input_meshes_clone in input_meshes_clones:
                    name_new = self.objectname_prefix + pivot_dummy_name + self.objectname_postfix
                    if 0 < len(name_new):
                        input_meshes_clone.name = name_new # will add numbering automatically
            
            print (" >> snapshots created: {}".format(input_meshes_clones))

            # do a view_layer refresh after creating clones
            bpy.context.view_layer.update()

            # post process (only!) clones -----

            # transfer modifier
            if True == transfer_modifier:
                print(" >> transfer (armature) modifier")
                MGTOOLS_functions_helper.transfere_modifier_armature(input_meshes, input_meshes_clones)

            # adopt pivot from pivot-dummy
            if True == self.set_pivots_to_dummy and None != to_export_pivot_dummy:
                print(" >> set pivot")
                MGTOOLS_functions_macros.set_pivot(
                    target_objects=input_meshes_clones, 
                    new_loc=to_export_pivot_dummy.location, 
                    new_rot_euler=to_export_pivot_dummy.rotation_euler, 
                    new_scale=to_export_pivot_dummy.scale,
                    apply_scale=True)

            # rename vertex groups
            if True == self.vgroups_rename:
                print(" >> rename vertex groups")
                for input_meshes_clone in input_meshes_clones:
                    MGTOOLS_functions_rename.rename_vertexgroups(
                        mesh_object=input_meshes_clone, 
                        mapping_file_path=self.vgroups_rename_mapping_file_path, 
                        mapping_invert=self.vgroups_rename_invert_mapping)

            # change modifier
            print(" >> preprocess modifier")
            for input_meshes_clone in input_meshes_clones:
                for mod in input_meshes_clone.modifiers:
                    # armatures
                    if 'ARMATURE' == mod.type:
                        # replacement armatures
                        if None != self.armature_replacement:
                            mod.object = self.armature_replacement

            # misc
            # for clone in input_meshes_clones:
                # parent mesh snapshots to pivot snapshot
                # if None != pivot_dummy_clone:
                #     MGTOOLS_functions_helper.set_parent(clone, pivot_dummy_clone, True)

            # rebuild to-export array
            if None != input_meshes_clones:
                to_export_meshes = input_meshes_clones + input_meshes_not_to_snapshot

        # cache original pivot-dummy transforms so we can revert it after export
        pivot_pos_cached = None
        pivot_rot_cached = None
        pivot_scale_cached = None
        if None != to_export_pivot_dummy:
            pivot_pos_cached = to_export_pivot_dummy.location.copy()
            pivot_rot_cached = to_export_pivot_dummy.rotation_euler.copy()
            pivot_scale_cached = to_export_pivot_dummy.scale.copy()
            # print ("Cached transforms: {}, {}".format(pivot_pos_cached, pivot_rot_cached))


        # options ----------------------------------
        # @ pivot dummy
        print (" > apply pivot dummy options")
        pivot_dummy_muted_constraints = []
        if None != to_export_pivot_dummy:
            # option: reset transforms
            if True == self.pivot_reset_location:
                print (" > exporting from origin")
                to_export_pivot_dummy.location = (0,0,0)
            if True == self.pivot_reset_rotation:
                to_export_pivot_dummy.rotation_euler = tuple(radians(a) for a in self.pivot_rotation)
            if True == self.pivot_reset_scale:
                to_export_pivot_dummy.scale = (1,1,1)
       
            # option: disable pivot dummy constraints
            self.export_pivot_dummy_disable_constraints = True
            if True == self.export_pivot_dummy_disable_constraints:
                print (" > muting pivot dummy constraints...")
                for constraint in to_export_pivot_dummy.constraints:
                    if False == constraint.mute:
                        print(" ... > {}".format(constraint.name))
                        pivot_dummy_muted_constraints.append(constraint)
                        constraint.mute = True

        # @ helper
        print (" > apply helper options")
        if True == self.export_helper_strip_dotnumbers:
            for helper in to_export_helper:
                last_dot_idx = helper.name.rfind('.')
                if 1 > last_dot_idx : continue
                stripped_name = helper.name[:last_dot_idx]
                helper.name = stripped_name
                # sometime blender requires to retry renaming the object a 2nd time (not sure why)
                if stripped_name != helper.name:
                    helper.name = stripped_name


        # for mesh in to_export_meshes:
        #     MGTOOLS_functions_macros.select_objects(mesh, True)
        #     bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

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
        self.filepath = self.build_filepath(self.path, self.filename_prefix + used_filename_prefix + self.filename + self.filename_postfix)

        # armature features
        armature_primary = None
        armature_primary_name_cached = ''
        if 0 < len(to_export_armatures):
            # we take the first armature in the list atm
            armature_primary = to_export_armatures[0]
            # rename armatures
            armature_primary_name_cached = armature_primary.name
            if '' != self.armature_primary_rename:
                armature_primary.name = self.armature_primary_rename

        # prepare anim related vars
        animation_strips_source = None
        animation_strips_source_active_action_cached = None

        # cache frame range
        cached_frame_start = bpy.context.scene.frame_start
        cached_frame_end = bpy.context.scene.frame_end

        if 'RANGE' == self.animation_export_mode:
            
            # this is kind of blenders default so we can just call export
            self.call_fbx_export() # < ============== EXPORT

        elif 'STRIPS' == self.animation_export_mode:
            # get object which holds animation strips information
            # Note: (here we are only interested on the frame ranges, not the actual animation data)
            for armature in to_export_armatures:
                if None == armature:
                    continue
                if None == armature.animation_data:
                    continue

                animation_strips_source = armature # to_export_armatures[0] if 0 < len(to_export_armatures) else None # for now we use the first armature
                animation_strips_source_active_action_cached = armature.animation_data.action
                break

            # if None != actions_source_override: # TODO: if this is somehow necessary the property needs to be added (or moved from the obsolete animation batch export)
            #     animation_strips_source = actions_source_override

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
                self.filepath = self.build_filepath(self.path, self.filename_prefix + self.filename_prefix_animation + self.filename + strip.action.name + self.filename_postfix)

                self.call_fbx_export() # < ============== EXPORT

        elif 'MARKERS' == self.animation_export_mode:
            
            marker_idx = -1
            current_start_marker_active = False
            current_start_marker_name = ''
            
            timeline_markers_sorted = bpy.context.scene.timeline_markers.values()
            timeline_markers_sorted.sort(key=lambda x: x.frame, reverse=False)

            # add fake end-marker to make sure there is newer a start marker the last marker
            timeline_markers_sorted.append(None)

            for marker in timeline_markers_sorted:
                marker_idx += 1

                marker_frame = marker.frame if None != marker else cached_frame_end
                marker_name = marker.name if None != marker else '__terminator__'

                # start marker of an animation
                is_start = 0 < len(self.animation_marker_start) and 0 <= marker_name.find(self.animation_marker_start)
                # end marker of an animation
                is_end = 0 < len(self.animation_marker_end) and 0 <= marker_name.find(self.animation_marker_end)
                # very last marker in the scene
                is_last = len(timeline_markers_sorted) - 1 == marker_idx

                print(" > marker {}: {}, is_start:{}, is_end:{}, is_last:{}, current anim:{}".format(marker_idx, marker_name, is_start, is_end, is_last, current_start_marker_name))

                # set start
                # special case: it's a start marker and the last marker at the same time
                # this is the only time we have to set this before the export call
                if True == is_start and True == is_last:
                    # set scene frame start
                    bpy.context.scene.frame_start = marker_frame
                    # set animation name for the following export
                    current_start_marker_active = True
                    current_start_marker_name = marker_name.replace(self.animation_marker_start, '')

                # set end
                if True == is_last:
                    # set scene frame end to the latest position we can analyse
                    bpy.context.scene.frame_end = cached_frame_end if cached_frame_end > bpy.context.scene.frame_start else marker_frame

                elif True == is_end:
                    # set scene frame end defined by the current end marker
                    bpy.context.scene.frame_end = marker_frame

                elif (True == is_start and True == current_start_marker_active):
                    # set scene frame end to be one frame before this new current start marker as this frame already belongs to the new animation
                    bpy.context.scene.frame_end = marker_frame-1

                # export
                # usually we export at every end marker - but there are some special cases:
                # - a start marker follows directly after a start marker (so serving as start and end marker at the same time)
                # - it's the last marker of the timeline (even if it's not a start nor end marker)
                # - a start marker which is also the last marker has another start marker in front (here we have to export both animations)
                if (True == is_start or True == is_end or True == is_last) and True == current_start_marker_active:
                    print(" > export now {}, from {} to {}".format(current_start_marker_name, bpy.context.scene.frame_start, bpy.context.scene.frame_end))

                    # update filename for animation export
                    self.filepath = self.build_filepath(self.path, self.filename_prefix + self.filename_prefix_animation + self.filename + current_start_marker_name + self.filename_postfix)

                    self.call_fbx_export() # < ============== EXPORT

                    # important: reset name
                    current_start_marker_active = False
                    current_start_marker_name = ''

                # set start
                if True == is_start and False == is_last:
                    # set scene frame start
                    bpy.context.scene.frame_start = marker_frame
                    # set animation name for the following export
                    current_start_marker_active = True
                    current_start_marker_name = marker_name.replace(self.animation_marker_start, '')

        elif 'OFF' == self.animation_export_mode:

            bpy.context.scene.frame_start = self.export_frame
            bpy.context.scene.frame_end = self.export_frame

            self.call_fbx_export() # < ============== EXPORT

        else:
            print('Unhandled animation export mode: {}.'.format(self.animation_export_mode))

        # cleanup ------------------------------------

        # revert armature name
        if None != armature_primary:
            armature_primary.name = armature_primary_name_cached

        # revert active action
        if None != animation_strips_source:
            animation_strips_source.animation_data.action = animation_strips_source_active_action_cached

        # revert scene frame range
        bpy.context.scene.frame_start = cached_frame_start
        bpy.context.scene.frame_end = cached_frame_end

        # revert pivot transforms
        if None != to_export_pivot_dummy:
            print(" > reverting pivot transforms")
            # print ("Cached transforms: {}, {}".format(pivot_pos_cached, pivot_rot_cached))
            to_export_pivot_dummy.location = pivot_pos_cached
            to_export_pivot_dummy.rotation_euler = pivot_rot_cached
            to_export_pivot_dummy.scale = pivot_scale_cached

            print(" > reverting pivot constraints")
            if 0 < len(pivot_dummy_muted_constraints):
                for constraint in pivot_dummy_muted_constraints:
                    constraint.mute = False

        # delete clones after export
        print(" > removing temporary export files")

        # if None != pivot_dummy_clone:
        #     bpy.data.objects.remove(pivot_dummy_clone)

        # remove cloned meshes
        if None != input_meshes_clones:
            for clone in input_meshes_clones:
                bpy.data.objects.remove(clone)

        # remove temporary export collections and their content
        if None != tmp_export_collection:
            for clone in tmp_export_collection.objects:
                bpy.data.objects.remove(clone)
            bpy.data.collections.remove(tmp_export_collection)

        # remove clones from collection instances made real
        if None != collection_instances_content_clones:
            while 0 < len(collection_instances_content_clones):
                clone = collection_instances_content_clones.pop(0)
                bpy.data.objects.remove(clone)

        # Reset selection
        bpy.context.view_layer.objects.active = active_object_cached
        MGTOOLS_functions_macros.select_objects(selected_objects_cached, False)

        # Reset edit mode
        if '' != active_mode_cached:
            bpy.ops.object.mode_set(mode=active_mode_cached)

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
            bake_anim_simplify_factor=self.bake_anim_simplify_factor,
        )

        # revert scene frame range
        bpy.context.scene.frame_start = cached_frame_start
        bpy.context.scene.frame_end = cached_frame_end
