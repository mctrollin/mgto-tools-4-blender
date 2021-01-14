from mathutils import Vector, Euler
import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty, FloatVectorProperty
from . mgtools_functions_helper import MGTOOLS_functions_helper

class MGTOOLS_properties_scene(PropertyGroup):


    # Properties.Rename ################################################################ 

    p_rename_mapping_file_path: StringProperty(name='Mapping file path', default="", description="Text file containing mapping in the format 'old_name:new_name;'", subtype='FILE_PATH',)
    p_rename_mapping_inverse: BoolProperty(name="Inverse mapping", default=False, description="Will invert the mapping direction in the mapping file from 'from:to: to 'to:from'",)


    # Properties.Rigging ################################################################ 

    p_rigging_bone_name_prefix: StringProperty(name='Bone name prefix', default="", description="Prefix added to all cloned bones",)
    p_rigging_add_root_bone: BoolProperty(name="Add root bone", default=False, description="Add root bone (0,0,0) and link bones without parent to it",)
    p_rigging_add_rotation_constraints_to_cloned_bones: BoolProperty(name="Add rotation constraints", default=False, description="Add to each bone a rotation constraint referencing the corresponding source bone",)

    p_rigging_constraints_retarget_target_armature: PointerProperty(name="Target", type=bpy.types.Object, description="New constraints target armature. ",)


    # Properties.Animation ################################################################ 

    # motion paths auto update  ---------------------
    p_motionpaths_is_auto_update_active: BoolProperty(name="Auto update", default=False, description="Automatically and periodically update motion paths",)
    p_motionpaths_auto_update_delay: FloatProperty(name="Delay", default=2, min=0.1, max=10.0, precision=1, subtype='FACTOR', description="Auto update delay", )

    p_animation_copy_data_source: PointerProperty(name="Source", type=bpy.types.Object, description="Animation data source object",)
    p_animation_copy_data_target: PointerProperty(name="Target", type=bpy.types.Object, description="Animation data target object",)


    # Properties.IO ################################################################ 

    # selection export ---------------------
    p_io_export_filepath: StringProperty(name='Export file', default="", description="Export file for selection export", subtype='FILE_PATH',)
   
    # collection export ---------------------
    p_io_export_folder_collections: StringProperty(name='Collections export folder', default="", description="Export folder path for collection bath export", subtype='DIR_PATH',)
    p_io_export_prefix_filter_collection: StringProperty(name='Filter: Collections', default="x_", description="Filter prefix for collections which should be exported",)
    p_io_export_prefix_filter_pivot: StringProperty(name='Filter: Pivot dummy', default="pivot_", description="Filter prefix for pivot dummies",)
    p_io_export_filename_prefix: StringProperty(name='Filename: Prefix', default="", description="Optional prefix",)
    p_io_export_filename_include_blendfilename: BoolProperty(name='Include .blend name', default=False, description="Include the filename of the currently open document in the export file name.",)

    # animation export ---------------------
    p_io_export_folder_animations: StringProperty(name='Animations export folder', default="", description="Export folder path for animations bath export", subtype='DIR_PATH',)
    p_io_export_actions_reference_override: PointerProperty(name="Action reference override", type=bpy.types.Object, description="Used as reference for action meta data. If not set the active object will be used.",)
    p_io_export_use_relative_frameranges: BoolProperty(name="Use relative frame ranges", default=True, description="Exported frame numbers will be relative to the exported action and not absolute to scene.",)
    p_io_export_animation_file_prefix: StringProperty(name='Animation file prefix', default="@", description="Prefix added to all exported animation files",)

    # hitboxes export ---------------------
    p_io_export_prefix_filter_collection_hitboxes: StringProperty(name='Filter: Collections', default="h_", description="Filter prefix for collections containing hitboxes data",)



    # shared settings ---------------------
    p_io_export_axis_forward: EnumProperty(
        name="Export forward axis",
        items=(
            ('X', "X", ""),
            ('-X', "-X", ""),
            ('Y', "Y", ""),
            ('-Y', "-Y", ""),
            ('Z', "Z", ""),
            ('-Z', "-Z", ""),
            ),
        default='-Z',
        description="Forward axis definition when exporting",
        )
    p_io_export_axis_up: EnumProperty(
        name="Export up axis", 
        items=(
            ('X', "X", ""),
            ('-X', "-X", ""),
            ('Y', "Y", ""),
            ('-Y', "-Y", ""),
            ('Z', "Z", ""),
            ('-Z', "-Z", ""),
            ),
        default='Y',
        description="Up axis definition when exporting",
        )
    p_io_export_include_pivot_dummy: BoolProperty(name="Include pivot dummy", default=True, description="Don't export the pivot dummy",)
    p_io_export_include_pivot_dummy_if_required: BoolProperty(name="Include pivot dummy if required", default=True, description="Don't export the pivot dummy if it's not necessary because we only export one single object",)
    p_io_export_set_pivots_to_dummy: BoolProperty(name="Set pivots to dummy", default=True, description="Will set all pivots to the pivot dummy transforms",)
    p_io_export_from_origin: BoolProperty(name="Move to origin", default=True, description="Export object from world origin",)
    p_io_export_alter_rotation: BoolProperty(name="Alter rotation", default=False, description="Change the rotation before exporting (and revert it afterwards)",)
    p_io_export_rotation: FloatVectorProperty(name="Export rotation", default=(0.0, 0.0, 0.0), description="Export object rotation",)
    p_io_export_use_mesh_modifiers: BoolProperty(name="Use mesh modifiers", default=True, description="Apply mesh modifiers during export (non-destructive)",)
    p_io_export_merge: BoolProperty(name="Combine meshes", default=True, description="Joins all related meshes together",)
    p_io_export_name_prefix: StringProperty(name='Object name prefix', default="m_", description="Prefix added to all exported meshes",)
    p_io_export_name_posfix: StringProperty(name='Object name posfix', default="", description="Posfix added to all exported meshes",)


    # Register ################################################################ 

    @classmethod
    def register(self):
        bpy.types.Scene.mgtools = PointerProperty(type=self)
    
    @classmethod
    def unregister(self):
        del bpy.types.Scene.mgtools




class MGTOOLS_properties_object(PropertyGroup):

    # Properties.Transforms ################################################################ 

    def get_world_location(self):
        # transform intrinsic- to world-space
        ao = bpy.context.view_layer.objects.active
        return MGTOOLS_functions_helper.get_world_location(ao)

    def set_world_location(self, value):
        # transform input world- to intrinsic-space
        ao = bpy.context.view_layer.objects.active
        if None == ao:
            return
        print("set_world_location: {} vs {}".format(value, ao.location))
        ao_pos_w = Vector(value)
        ao_pos_l = ao.parent.matrix_world.inverted() @ ao_pos_w
        ao_pos_i = ao.matrix_parent_inverse.inverted() @ ao_pos_l
        ao.location = ao_pos_i

    p_transforms_world_location: FloatVectorProperty(name="Pos (World)", subtype='TRANSLATION', get=get_world_location, set=set_world_location)

    def get_local_location(self):
        # transform intrinsic- to local-space
        ao = bpy.context.view_layer.objects.active
        return MGTOOLS_functions_helper.get_local_location(ao)

    def set_local_location(self, value):
        print("set_local_location: {}".format(value))
        # transform input world- to intrinsic-space
        ao = bpy.context.view_layer.objects.active
        if None == ao:
            return
        ao_pos_l = Vector(value)
        ao_pos_i = ao.matrix_parent_inverse.inverted() @ ao_pos_l
        ao.location = ao_pos_i

    p_transforms_local_location: FloatVectorProperty(name="Pos (Local)", subtype='TRANSLATION', get=get_local_location, set=set_local_location)

    def get_local_rotation(self):
        # transform intrinsic- to world-space
        ao = bpy.context.view_layer.objects.active
        if None == ao:
            return (0, 0, 0)
        ao_rot_l = ao.matrix_local.to_euler()
        return ao_rot_l

    def set_local_rotation(self, value):
        # transform input world- to intrinsic-space
        ao = bpy.context.view_layer.objects.active
        if None == ao:
            return
        print("set_local_rotation: {} vs {}".format(value, ao.rotation_euler))
        ao_rot_l = Euler(value)
        ao_rot_i = ao_rot_l
        ao_rot_i.rotate(ao.matrix_parent_inverse.inverted())
        ao.rotation_euler = ao_rot_i

    p_transforms_local_rotation: FloatVectorProperty(name="Rot (Local)", subtype='EULER', get=get_local_rotation, set=set_local_rotation)


    # Properties.Weight ################################################################ 

    # Weights display  --------------------- 
    def on_weightdisplay_isenabled(self, context):
        if True == self.p_weightdisplay_isenabled:
            bpy.ops.mgtools.weighting_show_weights('INVOKE_DEFAULT')
        else:
            bpy.ops.mgtools.weighting_hide_weights('INVOKE_DEFAULT')

    p_weightdisplay_isenabled: BoolProperty(name="Show Colored Vertices", default=False, description="Draw vertices in weights colors", update=on_weightdisplay_isenabled,)
    p_weightdisplay_point_size: IntProperty(name="Point Size", default=3, min=1, max=10, subtype='PIXEL', description="Point size", )
    p_weightdisplay_point_radius: FloatProperty(name="Point Radius", default=0.5, min=0.001, max=2.0, precision=3, subtype='FACTOR', description="Adjust point circular discard radius", )
    p_weightdisplay_global_alpha: FloatProperty(name="Point Alpha", default=1.0, min=0.0, max=1.0, precision=2, subtype='FACTOR', description="Adjust alpha of points displayed", )


    # Weights editing  ---------------------
    p_weightedit_add_amount: FloatProperty(name="Add", default=0.1, min=0.001, max=1.0, precision=3, subtype='FACTOR', description="Weight add amount", )

    p_weightedit_max_influences: IntProperty(name="Max Influences", default=3, min=1, max=100, description="Maximum amount of influences per vertex", )
    p_weightedit_min_weight: FloatProperty(name="Add", default=0.01, min=0.001, max=1.0, precision=3, subtype='FACTOR', description="Minimum influence strength per vertex", )
   
    p_weightedit_mirror_all_groups: BoolProperty(name="All Groups", default=True, description="Mirror weights from all groups", )
    p_weightedit_mirror_use_topology: BoolProperty(name="Use Topology", default=False, description="Use topology based mirroring (for when both sides of mesh have matching, unique topology)", )

    
    # Properties.Misc ################################################################ 

    # Snapshotting  ---------------------
    p_snapshot_frame_start: IntProperty(name="From", default=0, subtype='FACTOR', description="Start frame", )
    p_snapshot_frame_end: IntProperty(name="To", default=1, subtype='FACTOR', description="End frame", )
    p_snapshot_use_name_prefix: BoolProperty(name="Use Name Prefix", default=False, description="Use a custom name as prefix for the snapshots", )
    p_snapshot_merge_objects: BoolProperty(name="Merge", default=False, description="Merge all meshes of the snapshot", )
    p_snapshot_name_prefix: StringProperty(name='')


    # Register ################################################################ 

    @classmethod
    def register(self):
        bpy.types.Object.mgtools = PointerProperty(type=self)
    
    @classmethod
    def unregister(self):
        del bpy.types.Object.mgtools
