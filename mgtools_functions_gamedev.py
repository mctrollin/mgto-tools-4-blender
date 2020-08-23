from math import radians
import bpy
from mathutils import Euler, Quaternion # Matrix # Vector, Euler, 
from . mgtools_functions_helper import MGTOOLS_functions_helper

class MGTOOLS_functions_gamedev():

    @classmethod
    def get_hitboxes_string(self, objects):

        returnString = ""
        for obj in objects:

            print("Hitbox object = {}".format(obj.name))

            if None == obj:
                continue

            isCube = obj.name.startswith('Cube')
            isSphere = obj.name.startswith('Sphere')
            isCylinder = obj.name.startswith('Cylinder')

            if False == isCube and False == isSphere and False == isCylinder:
                continue

            scale = 1

            rot_tmp = obj.rotation_quaternion @ Euler((radians(90), 0, 0)).to_quaternion()
            rot = rot_tmp
            # convert into unity space (right handed to left handed quaternion) ########-
            rot.x = -rot_tmp.x
            rot.y = -rot_tmp.z
            rot.z = -rot_tmp.y
            rot.w = rot_tmp.w
            # mirror along y axis
            rot.x = -rot.x
            rot.z = -rot.z
            # ########
            print("rot: {} / {}".format(obj.rotation_quaternion, rot))

            pos = MGTOOLS_functions_helper.get_local_location(obj) * scale #(in coordsys parent obj.position)
            pos.x *= -1

            dimensions = obj.dimensions * scale

            # BOX hitbox
            if True == isCube:
                
                # convert to unity space (right handed to left handed dimension)
                tmpY = dimensions.y
                dimensions.y = dimensions.z
                dimensions.z = tmpY
                
                # change dimensons to match unity's system
                returnString += '<box>\n'
                returnString += '   <position x="{}" y="{}" z="{}" />\n'.format(pos.x, pos.y, pos.z)
                returnString += '   <size x="{}" y="{}" z="{}" />\n'.format(dimensions.x, dimensions.y, dimensions.z)
                returnString += '   <rotation x="{}" y="{}" z="{}" w="{}" />\n'.format(rot.x, rot.y, rot.z, rot.w)
                returnString += '</box>\n'
                
            # SPHERE hitbox
            elif True == isSphere:
            		
                dimensions.y = 0
                dimensions.z = 0
                
                returnString += '<sphere>\n'
                returnString += '   <position x="{}" y="{}" z="{}" />\n'.format(pos.x, pos.y, pos.z)
                returnString += '   <size x="{}" y="{}" z="{}" />\n'.format(dimensions.x, dimensions.y, dimensions.z)
                returnString += '</sphere>\n'
               
            # CYLINDER hitbox
            elif True == isCylinder:
            		
                dimensions.y =  dimensions.z
                dimensions.z = 0
                
                returnString += '<cylinder>\n'
                returnString += '   <position x="{}" y="{}" z="{}" />\n'.format(pos.x, pos.y, pos.z)
                returnString += '   <size x="{}" y="{}" z="{}" />\n'.format(dimensions.x, dimensions.y, dimensions.z)
                returnString += '   <rotation x="{}" y="{}" z="{}" w="{}" />\n'.format(rot.x, rot.y, rot.z, rot.w)
                returnString += '</cylinder>\n'
            
        
        return returnString	
