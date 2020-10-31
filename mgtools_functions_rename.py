import os
import math
import re

import bpy
from mathutils import Vector, Euler, Matrix
from . mgtools_functions_helper import MGTOOLS_functions_helper

class MGTOOLS_functions_rename():


    # Rename.Bones #######################################################

    @classmethod
    def rename_bones(self, armature_object, mapping_file_path, mapping_invert):
        
        if 'ARMATURE' != armature_object.type:
                return
        
        mapping_list = self.prepare_mapping_list(mapping_file_path)

        # loop through all bones
        for bone in armature_object.data.bones:
            # print ("Prosessing bone: {}".format(bone.name))

            # try get new name
            name_new = self.get_mapped_name(bone.name, mapping_list, mapping_invert)

            # apply new name 
            if "" != name_new:
                bone.name = name_new

    @classmethod
    def rename_vertexgroups(self, mesh_object, mapping_file_path, mapping_invert):
        
        if 'MESH' != mesh_object.type:
                return
        
        mapping_list = self.prepare_mapping_list(mapping_file_path)

         # loop through all vertex groups
        for vg in mesh_object.vertex_groups:
            # print ("Prosessing vertex group: {}".format(vg.name))

            # try get new name
            name_new = self.get_mapped_name(vg.name, mapping_list, mapping_invert)

            # apply new name 
            if "" != name_new:
                vg.name = name_new


    # Rename.Helper #######################################################

    @classmethod
    def get_mapped_name(self, name_input, mapping_list, mapping_invert):
        entries_count = math.floor(len(mapping_list)*0.5)
        # if entries_count % 2 > 0:
        #     print("Mapping file entry is missing")
        for i in range(entries_count):
            idx = i * 2
            if "" == name_input:
                continue
            if False == mapping_invert:
                if name_input == mapping_list[idx]:
                    return mapping_list[idx+1]
            else:
                if name_input == mapping_list[idx+1]:
                    return mapping_list[idx]
        return ""

    @classmethod
    def prepare_mapping_list(self, mapping_file_path):
        
        # checks
        if False == os.path.exists(mapping_file_path):
            return

        # read content of mapping file
        mapping_file = open(mapping_file_path,"r") 
        mapping_file_string = mapping_file.read() 
        mapping_file.close() 

        # split file string
        mapping_list =  re.split('[:;]', mapping_file_string)

        # remove white spaces
        for idx in range(len(mapping_list)):
            mapping_list[idx] = mapping_list[idx].strip()
        
        return mapping_list