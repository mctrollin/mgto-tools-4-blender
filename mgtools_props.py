# pyright: reportInvalidTypeForm=false

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
    p_rigging_add_location_constraints_to_cloned_bones: BoolProperty(name="Add location constraints", default=False, description="Add to each bone a location constraint referencing the corresponding source bone",)
    p_rigging_add_rotation_constraints_to_cloned_bones: BoolProperty(name="Add rotation constraints", default=False, description="Add to each bone a rotation constraint referencing the corresponding source bone",)
    p_rigging_add_scale_constraints_to_cloned_bones: BoolProperty(name="Add scale constraints", default=False, description="Add to each bone a scale constraint referencing the corresponding source bone",)


    p_rigging_bone_constraints_retarget_target: PointerProperty(name="Target", type=bpy.types.Object, description="New constraints target armature. ",)
    p_rigging_object_constraints_retarget_target: PointerProperty(name="Target", type=bpy.types.Object, description="New constraints target object. ",)

    # Properties.Animation ################################################################ 

    # motion paths auto update  ---------------------
    p_motionpaths_is_auto_update_active: BoolProperty(name="Auto update", default=False, description="Automatically and periodically update motion paths",)
    p_motionpaths_auto_update_delay: FloatProperty(name="Delay", default=2, min=0.1, max=10.0, precision=1, subtype='FACTOR', description="Auto update delay", )

    p_animation_copy_data_source: PointerProperty(name="Source", type=bpy.types.Object, description="Animation data source object",)
    p_animation_copy_data_target: PointerProperty(name="Target", type=bpy.types.Object, description="Animation data target object",)


    # Properties.IO ################################################################ 

    # axis
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
    p_io_export_primary_bone_axis: EnumProperty(
        name="Primary bone axis",
        items=(
            ('X', "X", ""),
            ('-X', "-X", ""),
            ('Y', "Y", ""),
            ('-Y', "-Y", ""),
            ('Z', "Z", ""),
            ('-Z', "-Z", ""),
            ),
        default='Y',
        description="Primary bone axis definition when exporting",
        )
    p_io_export_secondary_bone_axis: EnumProperty(
        name="Secondary bone axis",
        items=(
            ('X', "X", ""),
            ('-X', "-X", ""),
            ('Y', "Y", ""),
            ('-Y', "-Y", ""),
            ('Z', "Z", ""),
            ('-Z', "-Z", ""),
            ),
        default='X',
        description="Secondary bone axis definition when exporting",
        )

    p_io_export_scale_apply_options: EnumProperty(
        name="Apply Scalings",
        items=(
            ('FBX_SCALE_NONE', "All Local", "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0."),
            ('FBX_SCALE_UNITS', "FBX Units Scale", "Apply custom scaling to each object transformation, and units scaling to FBX scale."),
            ('FBX_SCALE_CUSTOM', "FBX Custom Scale", "Apply custom scaling to FBX scale, and units scaling to each object transformation."),
            ('FBX_SCALE_ALL', "FBX All", "Apply custom scaling and units scaling to FBX scale."),
            ),
        default='FBX_SCALE_ALL',
        description="How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way)",
        )
    p_io_export_scale: FloatProperty(name="Scale", default=1, description="Scale all data (Some importers do not support scaled armatures!).",)
    p_io_export_apply_unit_scale: BoolProperty(name="Apply Unit", default=True, description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is).",)
    p_io_export_use_space_transform: BoolProperty(name="Use Space Transform", default=True, description="Apply global space transform to the object rotations. When disabled only the axis space is written to the file and all object transforms are left as-is.",)
    

    # pivot
    p_io_export_prefix_filter_pivot: StringProperty(name='Filter: Pivot dummy', default="pivot_", description="Filter prefix for pivot dummies.",)
    p_io_export_include_pivot_dummy: BoolProperty(name="Include pivot dummy", default=True, description="Don't export the pivot dummy.",)
    p_io_export_include_pivot_dummy_if_required: BoolProperty(name="Include pivot dummy if required", default=True, description="Don't export the pivot dummy if it's not necessary because we only export one single object.",)
    p_io_export_set_pivots_to_dummy: BoolProperty(name="Set pivots to dummy", default=True, description="Will set all pivots to the pivot dummy transforms.",)
    p_io_export_pivot_reset_location: BoolProperty(name="Revert Location", default=True, description="Export object from world origin.",)
    p_io_export_pivot_reset_rotation: BoolProperty(name="Revert Rotation", default=False, description="Export object without rotation (except offset).",)
    p_io_export_pivot_reset_scale: BoolProperty(name="Revert Scale", default=False, description="Export object without scale.",)
    p_io_export_rotation: FloatVectorProperty(name="Export rotation offset", default=(0.0, 0.0, 0.0), description="Export object rotation.",)
    p_io_export_pivot_dummy_disable_constraints: BoolProperty(name="Disable constraints", default=False, description="Disable constraints on the pivot dummy.",)

    #helper
    p_io_export_helper_strip_dotnumbers: BoolProperty(name="Strip dot-numbers", default=False, description="Try to remove blenders .000 numbering on helper objects.",)

    # mesh
    p_io_export_use_mesh_modifiers: BoolProperty(name="Apply modifiers", default=True, description="Apply mesh modifiers during export (excluding armature modifier, non-destructive).",)
    p_io_export_use_mesh_modifiers_armature: BoolProperty(name="Apply armature", default=False, description="Apply armature modifiers during export (non-destructive).",)
    p_io_export_mesh_smooth_type: EnumProperty(
        name="Smoothing",
        items=(
            ('OFF', "Normals Only", "Export only normals instead of writing edge or face smoothing data"),
            ('FACE', "Face", "Write face smoothing"),
            ('EDGE', "Edge", "Write edge smoothing"),
            ),
        default='OFF',
        description="Export smoothing information (prefer ‘Normals Only’ option if your target importer understand split normals)",
        )
    p_io_export_combine_meshes: BoolProperty(name="Combine meshes", default=True, description="Joins all related meshes together.",)
    p_io_export_clone_meshes_filter: StringProperty(name='Clone meshes filter', default="", description="Allows to exclude meshes from beeing cloned. Usually this should be off but allows to export models as-is in specific situations where a complex object setup doesn't survive the cloning process. Delimiter=','.",)
    p_io_export_combine_meshes_filter: StringProperty(name='Combine meshes filter', default="", description="Allows to exclude meshes from beeing combined during export when 'Combine meshes' option is enabled. Delimiter=','.",)
    p_io_export_objectname_prefix: StringProperty(name='Object name prefix', default="m_", description="Prefix added to all cloned meshes.",)
    p_io_export_objectname_postfix: StringProperty(name='Object name postfix', default="", description="Postfix added to all cloned meshes.",)
    p_io_export_vgroups_rename: BoolProperty(name="Rename Vertex Groups", default=False, description="Rename vertex groups based on a mapping file.",)
    p_io_export_vgroups_rename_mapping_file_path: StringProperty(name='Mapping file path', default="", description="Text file containing mapping in the format 'old_name:new_name;'", subtype='FILE_PATH',)
    p_io_export_vgroups_rename_mapping_inverse: BoolProperty(name="Inverse mapping", default=False, description="Will invert the mapping direction in the mapping file from 'from:to: to 'to:from'",)
    p_io_export_armature_replacement: PointerProperty(name="Armature Replacement", type=bpy.types.Object, description="For clones it will replace any possible armature reference inside armature modifier.",)
    p_io_export_weights_limit: IntProperty(name='Bone influence limit', default=4, description="Limits the number of weights per vertex. -1 means unlimited.",)

    # filename
    p_io_export_filename_prefix: StringProperty(name='Filename: Prefix', default="", description="Optional filename prefix.",)
    p_io_export_filename_prefix_static: StringProperty(name='Filename: Prefix (static)', default="", description="Optional filename prefix for static meshes.",)
    p_io_export_filename_prefix_skeletal: StringProperty(name='Filename: Prefix (skeletal)', default="", description="Optional filename prefix for skeletal meshes.",)
    p_io_export_filename_prefix_animation: StringProperty(name='Filename: Prefix (animation)', default="", description="Optional filename prefix for animations.",)
    p_io_export_filename_postfix: StringProperty(name='Filename: Postfix', default="", description="Optional filename postfix.",)
    p_io_export_filename_include_blendfilename: BoolProperty(name='Include .blend name', default=False, description="Include the filename of the currently open document in the export file name.",)
    p_io_export_filename_ignore_collection_dot_prefix: BoolProperty(name='Ignore .000', default=False, description="Excludes everything after the last dot in the collection name (e.g. 'bla.blub' will become just 'bla').",)

    # armature
    p_io_export_armature_rename: StringProperty(name='Armature temp export name', default="", description="Allows to rename the primary armature during export. Will be reverted afterwards.",)

    # animation
    p_io_export_animation_mode: EnumProperty(
        name="Framerange mode",
        items=(
            ('OFF', 'OFF', 'Export just a single frame.'),
            ('STRIPS', 'STRIPS', 'Export is based on animation strips.'),
            ('MARKERS', 'MARKERS', 'Export will use markers to find and output one or multiple animation sequences.'),
            ('RANGE', 'RANGE', 'Export one animation defined by the playback range'),
            ),
        default='OFF',
        description="Mode for finding animation frame ranges for exporting",
        )
    p_io_export_frame: IntProperty(name='Export Frame', default=0, description="Export frame number if animation export is disabled.",)
    p_io_export_animation_use_relative_frameranges: BoolProperty(name="Use relative frame ranges", default=True, description="Exported frame numbers will be relative to the exported action and not absolute to scene.",)
    p_io_export_animation_marker_start: StringProperty(name='Filter: Marker Start', default="x_", description="Filter string for to-export frame range start marker.",)
    p_io_export_animation_marker_end: StringProperty(name='Filter: Marker End', default="_END", description="Filter string for to-export frame range end marker.",)
    p_io_export_animation_bake_anim_simplify_factor: FloatProperty(name="Anim Simplify", default=0.0, description="How much to simplify baked values (0.0 to disable, the higher the more simplified).",)

    # material
    p_io_export_material_override: PointerProperty(name="Mat Override", type=bpy.types.Material, description="Material override - will add new material slot or replace any existing slot with this material.",)

    # selection export ---------------------
    p_io_export_filepath: StringProperty(name='Export file', default="", description="Export file for selection export.", subtype='FILE_PATH',)
   
    # collection export ---------------------
    p_io_export_folder_collections: StringProperty(name='Collections export folder', default="", description="Export folder path for collection bath export.", subtype='DIR_PATH',)
    p_io_export_prefix_filter_collection: StringProperty(name='Filter: Collections', default="x_", description="Filter prefix for collections which should be exported.",)

    # animation export (legacy) ---------------------
    p_io_export_animation_folder: StringProperty(name='Animations export folder', default="", description="Export folder path for animations bath export.", subtype='DIR_PATH',)
    p_io_export_animation_actions_reference_override: PointerProperty(name="Action reference override", type=bpy.types.Object, description="Used as reference for action meta data. If not set the active object will be used.",)

    # hitboxes export ---------------------
    p_io_export_prefix_filter_collection_hitboxes: StringProperty(name='Filter: Collections', default="h_", description="Filter prefix for collections containing hitboxes data.",)


    # Properties.Misc ################################################################ 

    p_particle_hair_to_mesh_thickness: FloatProperty(name="Thickness", default=0.0001, min=0.00001, max=1000.0, precision=5, subtype='FACTOR', description="The hair tickness when converting the particle hair to a mesh.", )
    p_particle_hair_to_mesh_resolution: FloatProperty(name="Resolution", default=0, min=0, max=100, precision=0, subtype='FACTOR', description="The hair resolution when converting the particle hair to a mesh.", )
    p_particle_hair_to_mesh_name: StringProperty(name="Name", default="HairMesh", description="Basename of all hair mesh objects which will be created.", )

    p_modifier_toggle_name: StringProperty(name="Mod Name", default="Mirror", description="Modifier Name", )
    p_modifier_toggle_name_2: StringProperty(name="Mod Name", default="Mirror", description="Modifier Name", )
    p_modifier_toggle_name_3: StringProperty(name="Mod Name", default="Mirror", description="Modifier Name", )

    p_attributes_vertex_positions_snapshot_name: StringProperty(name="Vertex Positions Snapshot", default="vert_pos_snapshot", description="Attribute name for vertex position snapshot", )
    p_attributes_vertex_positions_snapshot_relative: BoolProperty(name="Relative", default=True, description="Defines if the snapshotted values are absolute or offsets from the base vertex position.",)

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
    p_weightedit_average_factor: FloatProperty(name="Factor", default=1.0, min=0.001, max=1.0, precision=3, subtype='FACTOR', description="Weight average factor, 0: no change, 0.5: 50% between current and average, 1: average", )

    p_weightedit_remove_empty: BoolProperty(name="Remove only Empty", default=True, description="Will remove only empty vertex groups", )
    p_weightedit_remove_locked: BoolProperty(name="Remove also Locked", default=False,  description="Remove also locked vertex groups", )

    p_weightedit_max_influences: IntProperty(name="Max Influences", default=3, min=1, max=100, description="Maximum amount of influences per vertex", )
    p_weightedit_min_weight: FloatProperty(name="Add", default=0.01, min=0.001, max=1.0, precision=3, subtype='FACTOR', description="Minimum influence strength per vertex", )
   
    p_weightedit_mirror_all_groups: BoolProperty(name="All Groups", default=True, description="Mirror weights from all groups", )
    p_weightedit_mirror_use_topology: BoolProperty(name="Use Topology", default=False, description="Use topology based mirroring (for when both sides of mesh have matching, unique topology)", )

    p_weightedit_list_enabled: BoolProperty(name="Show weights list", default=False, description="Show weights list ui widget. Can be slow with many vertex groups.", update=on_weightdisplay_isenabled,)
    
    p_weightedit_copy_vg: StringProperty(name='')

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
