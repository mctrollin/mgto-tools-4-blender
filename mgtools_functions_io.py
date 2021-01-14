import os
import bpy


class MGTOOLS_functions_io():

    @classmethod
    def build_filepath(self, path, filename, extension):
        return path + '\\' + filename + '.' + extension

    @classmethod
    def check_permissions(self, path):
        if not os.path.exists(path):
            return True
        return os.access(path, os.W_OK)

    @classmethod
    def prepare_export(self, path):
        # prepare path
        print ("Check and prepare directory: " + path)
        if not os.path.exists(path):
            os.mkdir(path)


    @classmethod
    def export_textfile(self, path, name, extension, string):
        
        # create directory if necessary
        self.prepare_export(path)

        # build full file path
        filepath = self.build_filepath(path, name, extension)

        print("export_textfile: {} data:{}".format(filepath, string))

        # create file and write data 
        with open(filepath, 'w') as out_file:
            out_file.write(string)