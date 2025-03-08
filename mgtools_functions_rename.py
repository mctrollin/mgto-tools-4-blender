import os
import math
import re

import bpy
from mathutils import Vector, Euler, Matrix
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

class MGTOOLS_functions_rename():


    # Rename.Bones #######################################################

    @classmethod
    def rename_bones(self, armature_object, mapping_file_path, mapping_invert):
        
        if 'ARMATURE' != armature_object.type:
            print("No armature")
            return
        
        mapping_list = self.prepare_mapping_list(mapping_file_path)
        if None == mapping_list: 
            print("No mapping file")
            return
        if False == isinstance(mapping_list, list):
            print("Invalid mapping file")
            return
        if 0 >= len(mapping_list):
            print("No mapping entries")
            return

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
            print("No mesh")
            return
        
        mapping_list = self.prepare_mapping_list(mapping_file_path)
        if None == mapping_list:
            print("No mapping file")
            return
        if False == isinstance(mapping_list, list):
            print("Invalid mapping file")
            return
        if 0 >= len(mapping_list):
            print("No mapping entries")
            return

        # mapping based loop
        # loop through mapping list
        entries_count = math.floor(len(mapping_list)*0.5)
        name_from = ''
        name_to = ''
        for i in range(entries_count):
            idx = i * 2
            if False == mapping_invert:
                name_from = mapping_list[idx]
                name_to = mapping_list[idx+1]
            else:
                name_from = mapping_list[idx+1]
                name_to = mapping_list[idx]

            
            # apply new name 
            if 0 <= mesh_object.vertex_groups.find(name_from):
                vg_from = mesh_object.vertex_groups[name_from]
                if "" != name_from and name_from != name_to:
                    # use existing
                    if 0 <= mesh_object.vertex_groups.find(name_to):
                        MGTOOLS_functions_macros.transfer_weights(vg_from, mesh_object.vertex_groups[name_to], mesh_object.data)
                        mesh_object.vertex_groups.remove(vg_from)
                    # rename
                    else:
                        vg_from.name = name_to

                    # rename vertex groups in modifiers
                    for mod in mesh_object.modifiers:
                        if hasattr(mod, 'vertex_group'):
                            if name_from == mod.vertex_group:
                                mod.vertex_group = name_to

        # vertex-group based loop
        # # loop through all vertex groups
        # for vg in mesh_object.vertex_groups:
        #     # print ("Prosessing vertex group: {}".format(vg.name))

        #     # try get new name
        #     name_new = self.get_mapped_name(vg.name, mapping_list, mapping_invert)

        #     # apply new name 
        #     if "" != name_new and vg.name != name_new:
        #         # use existing
        #         if 0 <= mesh_object.vertex_groups.find(name_new):
        #             MGTOOLS_functions_macros.transfer_weights(vg, mesh_object.vertex_groups[name_new], mesh_object.data)
        #             mesh_object.vertex_groups.remove(vg)
        #         # rename
        #         else:
        #             vg.name = name_new

    @classmethod
    def rename_fcurves(self, object, mapping_file_path, mapping_invert):

        if not object:
            print("No object")
            return

        mapping_list = self.prepare_mapping_list(mapping_file_path)
        if None == mapping_list:
            print("No mapping file")
            return
        if False == isinstance(mapping_list, list):
            print("Invalid mapping file")
            return
        if 0 >= len(mapping_list):
            print("No mapping entries")
            return

        action = object.animation_data.action
        if action:
            for fc in action.fcurves:
                name = self.get_bonename_from_fcurve_datapath(fc.data_path)
                if name:
                    new_name = self.get_mapped_name(name, mapping_list, mapping_invert)
                    if new_name:
                        fc.data_path = fc.data_path.replace(name, new_name)
                        if fc.group:
                            fc.group.name = new_name
                        else:
                            fc.group = (
                                    action.groups.get(new_name) 
                                    or
                                    action.groups.new(new_name)
                                    )

    # Rename.Helper #######################################################

    @classmethod
    def get_mapped_name(self, name_input, mapping_list, mapping_invert):
        if False == isinstance(mapping_list, list):
            print("Invalid mapping list")
            return
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
        
        mapping_file_path_absolute = bpy.path.abspath(mapping_file_path)

        # checks
        if False == os.path.exists(mapping_file_path_absolute):
            return

        # read content of mapping file
        mapping_file = open(mapping_file_path_absolute,"r") 
        mapping_file_string = mapping_file.read() 
        mapping_file.close() 

        # pre-split
        mapping_list = []

        mapping_file_string_lines = mapping_file_string.splitlines()
        for mapping_file_string_line in mapping_file_string_lines:
            mapping_list_pre =  re.split('[;]', mapping_file_string_line)

            for tmp_str in mapping_list_pre:
                if not tmp_str: continue
                if '//' in tmp_str: continue
                if ':' not in tmp_str: continue
                mapping_list.extend(tmp_str.split(':'))


        # split file string
        #mapping_list =  re.split('[:;]', mapping_file_string)

        # remove white spaces
        for idx in range(len(mapping_list)):
            mapping_list[idx] = mapping_list[idx].strip()
        
        return mapping_list

    @classmethod
    def get_bonename_from_fcurve_datapath(self, data_path):
        if not data_path.startswith("pose.bones"):
            return None
        start = data_path.find('["') + 2
        end = data_path.find('"]') 
        return data_path[start : end]