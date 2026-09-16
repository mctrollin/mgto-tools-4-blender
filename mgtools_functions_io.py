import os
import bpy
from . mgtools_functions_helper import MGTOOLS_functions_helper

class MGTOOLS_functions_io():

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