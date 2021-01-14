import bpy
from bpy.types import Operator
from math import radians
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

# we use this for simple debug tests
class MGTOOLS_OT_sandbox_debug1(Operator):
    bl_idname = "mgtools.sandbox_debug1"
    bl_label = "mgtools test operator"
    bl_description = "Debug test 1"

    def execute(self, context):

        # print("Test properties: {}".format(bpy.types.Scene.mgtools.p_weightdisplay_point_size))


        # ---------------------------------------------
        # TEST: rotation
        # rot_degree = (90, 0, 0)
        # bpy.context.view_layer.objects.active.rotation_euler = tuple(radians(a) for a in rot_degree)

        # ---------------------------------------------
        # TEST: list creation
        # print(([0] * 5))
        # print(*([0] * 5))


        # ---------------------------------------------
        # TEST: binary packing and unpacking
        # import struct
        # binary_data = struct.pack("7L", 6, 9, *([0] * 5))
        # print(binary_data)
        # # When unpacking, you receive a tuple of all data in the same order
        # tuple_of_data = struct.unpack("7L", binary_data)
        # print(tuple_of_data)


        # ---------------------------------------------
        # TEST: vertex coordinate scaling
        # scale = 0.5
        # vert_coord = (0.4, 4.6, 6.8)
        # vert_coord_scaled = [a * scale for a in vert_coord]
        # print(vert_coord_scaled)


        # ---------------------------------------------
        # TEST: mesh snapshot
        # meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        # MGTOOLS_functions_macros.make_snapshot_from(meshobj)
        # MGTOOLS_functions_macros.select_only(meshobj)


        # ---------------------------------------------
        # TEST: read uvs from bmesh
        # meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        # import bmesh
        # # Get a BMesh representation
        # bm = bmesh.new()
        # bm.from_mesh(meshobj.data)
        # # triangulate (for exporter sanity)
        # bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='SHORT_EDGE', ngon_method='BEAUTY')        
        # uv_chan_count = len(bm.loops.layers.uv)
        # for face in bm.faces:
        #     print("Face {}: verts:{}".format(face.index, face.verts[:]))
        #     for loop in face.loops:
        #         for i in range(0,2):
        #             uv = (0,0)
        #             if uv_chan_count > i:
        #                 uv = loop[bm.loops.layers.uv[i]].uv
        #             print("UVs{}: vert index:{} uvs:{}".format(i, loop.vert.index, uv[:]))    
        #             # restrict to 0-1 range
        #             uv[0] = uv[0] % 1
        #             uv[1] = uv[1] % 1
        #             print("UVs{}: vert index:{} uvs:{}".format(i, loop.vert.index, uv[:]))                   
        # bm.free()

        # ---------------------------------------------
        # TEST: read verts from bmesh
        # meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        # import bmesh
        # # Get a BMesh representation
        # bm = bmesh.new()
        # bm.from_mesh(meshobj.data)
        # # triangulate (for exporter sanity)
        # bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='SHORT_EDGE', ngon_method='BEAUTY')
        # print("Verts count: {}".format(len(bm.verts)))
        # # for i, v in enumerate(bm.verts):
        # #     print("I: {} V:{}".format(i,v.index))
        # for i, poly in enumerate(bm.faces):
        #     print("Face: {} verts: {}".format(i, len(poly.verts)))
        #     verts_indices = ()
        #     verts_indices = [vert.index for vert in poly.verts]
        #     print(verts_indices)
        #     # for k, vert in enumerate(poly.verts):
        #     #     print("#: {} V:{}".format(k, vert.index))
        # bm.free()


        # ---------------------------------------------
        # TEST: copy to new collection
        # MGTOOLS_functions_macros.duplicate_to_collection(bpy.context.selected_objects, False)
        MGTOOLS_functions_macros.make_collection_instance_real(bpy.context.view_layer.objects.active)

        # ---------------------------------------------
        return{'FINISHED'}

        
