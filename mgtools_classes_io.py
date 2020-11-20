import os
from math import radians
import bpy
from mathutils import Matrix # Vector, Euler, 
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
from . mgtools_functions_io import MGTOOLS_functions_io

class MGTOOLS_io_exporter():

    # mandatory settings
    path = ""
    filename = ""
    filepath = ""
    axis_forward = '-Z'
    axis_up = 'Y'
    use_mesh_modifiers = True

    # selection based options
    to_export_selection = []

    # collection based options
    to_export_collection = None
    pivot_dummy_prefix = ""
    include_pivot_dummy = True
    include_pivot_dummy_if_required = False
    set_pivots_to_dummy = True

    # optional settings
    combine_meshes = False
    export_from_origin = False
    alter_pivot_rotation = False
    pivot_rotation = (0,0,0)
    prefix = "to_export__"


    def __init__(self, path, filename):
        self.path = path
        self.filename = filename

        # construct export file path
        self.path = bpy.path.abspath(self.path)
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

        self.export_now(self.to_export_selection)

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

        self.export_now(self.to_export_collection.all_objects)

        print(" > Export (collection) finished for " + self.filepath)

    def build_filepath(self, path, filename):
        return path + '\\' + filename + '.fbx'

    def prepare_export(self, path):
        # prepare path
        print ("Check and prepare directory: " + path)
        if not os.path.exists(path):
            os.mkdir(path)

    def export_now(self, input_objects):
        
        print ("Export now: {}".format(input_objects))

        # tmp: decide if we should create throw-away only-for-export clones or not
        # create_clones = False
        # if True == self.combine_meshes:
        #     create_clones = True
        create_clones = True

        # checks ----------------------------------
        if None == input_objects:
            print(" > error: No objects defined for export")
            return


        # prepare ----------------------------------
        # filter objects into separate lists and try to find pivot dummy
        input_meshes = []
        input_helper = []
        input_armatures = []
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
                else:
                    input_helper.append(obj)
            # everythin else
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
        if True == create_clones:
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
            input_meshes_clones = MGTOOLS_functions_macros.make_snapshot_from(input_meshes, self.combine_meshes, self.prefix, False, None)
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
            use_armature_deform_only=False,
            armature_nodetype='NULL', # 'ROOT' gives good results if only exporting an armature
            # anim 
            bake_anim=True,
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



        # cleanup ------------------------------------

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

    @classmethod
    def quick_export_anim(self, path, filename, frame_start, frame_end):

        self.prepare_export(self, path)
        filepath = self.build_filepath(self, path, filename)
        
        if False == MGTOOLS_functions_io.check_permissions(filepath):
            print (" > Permission denied.")
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
            use_armature_deform_only=False,
            armature_nodetype='NULL', # 'ROOT' gives good results if only exporting an armature
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
