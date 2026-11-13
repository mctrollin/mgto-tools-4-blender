import os
import bpy
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_vertex_color import MGTOOLS_functions_vertex_color

class MGTOOLS_functions_io():

    @classmethod
    def bake_to_vcolors_on_clones(self, mesh_objects, attribute_name, channel_modes, samples, objects_to_hide=()):
        """Apply configured bake modes to export clones' vertex colors."""
        if not any(channel != 'OFF' for channel in channel_modes):
            return
        print(" >> bake to vertex color")
        for mesh_object in mesh_objects:
            render_visibility = {}
            # AO rays should see the active export clone, but not its source or sibling clones.
            objects_to_hide_for_bake = set(objects_to_hide) | set(mesh_objects)
            objects_to_hide_for_bake.discard(mesh_object)
            for object_to_hide in objects_to_hide_for_bake:
                render_visibility[object_to_hide] = object_to_hide.hide_render
                object_to_hide.hide_render = True
            try:
                for channel_index, bake_type in enumerate(channel_modes):
                    if bake_type == 'OFF':
                        continue
                    if bake_type.startswith('VALUE_'):
                        value = {
                            'VALUE_0': 0.0,
                            'VALUE_025': 0.25,
                            'VALUE_050': 0.5,
                            'VALUE_075': 0.75,
                            'VALUE_1': 1.0,
                        }[bake_type]
                        MGTOOLS_functions_vertex_color.write_vcolors_attribute_channel(
                            obj=mesh_object, 
                            attribute_name=attribute_name, 
                            channel=channel_index, 
                            value=value)
                    else:
                        MGTOOLS_functions_vertex_color.bake_to_vcolors_attribute(
                            obj=mesh_object,
                            bake_type=bake_type,
                            attribute_name=attribute_name,
                            channel=channel_index,
                            samples=samples)
            finally:
                # Export baking must not leave the user's scene with changed render visibility.
                for object_to_hide, hide_render in render_visibility.items():
                    object_to_hide.hide_render = hide_render

    @classmethod
    def build_filepath(self, path, filename, extension):
        """Build a Windows-style filepath from a directory, filename, and extension."""
        return path + '\\' + filename + '.' + extension

    @classmethod
    def check_permissions(self, path):
        """Return whether the directory exists and is writable, or can be created."""
        if not os.path.exists(path):
            return True
        return os.access(path, os.W_OK)

    @classmethod
    def prepare_export(self, path):
        """Create the export directory when it does not already exist."""
        # prepare path
        print ("Check and prepare directory: " + path)
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def export_textfile(self, path, name, extension, string):
        """Prepare an export directory and write text data to the requested file."""
        
        # create directory if necessary
        self.prepare_export(path)

        # build full file path
        filepath = self.build_filepath(path, name, extension)

        print("export_textfile: {} data:{}".format(filepath, string))

        # create file and write data 
        with open(filepath, 'w') as out_file:
            out_file.write(string)

    @classmethod
    def get_export_skip_reasons(self, obj, collection=None):
        """Return visibility/selectability reasons for skipping an export object."""
        if None == obj:
            return ['object is missing']
        reasons = []
        if obj.hide_viewport:
            reasons.append('Object.hide_viewport')
        if obj.hide_select:
            reasons.append('Object.hide_select')
        object_base = bpy.context.view_layer.objects.get(obj.name)
        if None != object_base and object_base.hide_viewport:
            reasons.append('ObjectBase.hide_viewport')

        collections = ([collection] + list(obj.users_collection) 
                       if None != collection and None != collection.all_objects.get(obj.name)
                       else list(obj.users_collection))
        checked_collections = set()
        for obj_collection in collections:
            if None == obj_collection or obj_collection in checked_collections:
                continue
            checked_collections.add(obj_collection)
            if obj_collection.hide_viewport:
                reasons.append('Collection.hide_viewport')
            if obj_collection.hide_select:
                reasons.append('Collection.hide_select')
            layer_path = MGTOOLS_functions_helper.get_layercollection_path(obj_collection)
            if None != layer_path:
                for layer_collection in layer_path:
                    if layer_collection.exclude:
                        reasons.append('LayerCollection.exclude')
                    if layer_collection.hide_viewport:
                        reasons.append('LayerCollection.hide_viewport')
        return list(dict.fromkeys(reasons))

    @classmethod
    def filter_export_objects(self, objects, collection=None):
        """Filter objects and return (exportable_objects, skipped_object_reasons)."""
        exportable_objects = []
        skipped_object_reasons = {}
        for obj in objects:
            reasons = self.get_export_skip_reasons(obj, collection)
            if 0 < len(reasons):
                skipped_object_reasons[obj] = reasons
            else:
                exportable_objects.append(obj)
        return exportable_objects, skipped_object_reasons

    @classmethod
    def get_skipped_armatures(self, objects, collection=None):
        """Return skipped armatures found directly or through armature modifiers."""
        skipped_armatures = {}
        candidates = []
        for obj in objects:
            if 'ARMATURE' == obj.type:
                candidates.append(obj)
            for mod in obj.modifiers:
                if 'ARMATURE' == mod.type and None != mod.object:
                    candidates.append(mod.object)
        for armature in candidates:
            reasons = self.get_export_skip_reasons(armature, collection)
            if 0 < len(reasons):
                skipped_armatures[armature] = reasons
        return skipped_armatures