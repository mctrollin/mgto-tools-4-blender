import bpy
from bpy.types import Operator
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros
import fnmatch

class MGTOOLS_OT_match_vertex_groups(Operator):
    bl_idname = "mgtools.match_vertex_groups"
    bl_label = "Match Vertex Groups"
    bl_description = "Match vertex group names and order from active object to all selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("MGTOOLS_OT_match_vertex_groups")

        obj_active = context.view_layer.objects.active
        if None == obj_active:
            print("No active object found")
            return {'CANCELLED'}

        if 'MESH' != obj_active.type:
            print("Active object is not a mesh")
            return {'CANCELLED'}

        objs_selected = context.selected_objects
        if None == objs_selected or 1 >= len(objs_selected):
            print("No other selected objects to match")
            return {'CANCELLED'}

        # read properties -----------------------------------
        mgtools_props_scene = bpy.context.scene.mgtools

        keep_target_unique = mgtools_props_scene.p_mesh_keep_target_unique_vgs
        copy_flags = mgtools_props_scene.p_mesh_copy_vg_flags

        # source vertex group names in order
        vgs_names_source = [vg.name for vg in obj_active.vertex_groups]
        print(f"Source ({obj_active.name}) vertex groups: {vgs_names_source}")

        # parse filter patterns (comma-separated wildcards, case-sensitive)
        vg_filter_raw = mgtools_props_scene.p_mesh_vg_name_filter if hasattr(mgtools_props_scene, 'p_mesh_vg_name_filter') else ''
        vg_patterns = [p.strip() for p in vg_filter_raw.split(',') if p.strip()]
        def vg_matches(name):
            if not vg_patterns:
                return True
            for pat in vg_patterns:
                if fnmatch.fnmatchcase(name, pat):
                    return True
            return False

        # determine which source VGs are processed
        processed_source = [n for n in vgs_names_source if vg_matches(n)]
        if 0 >= len(processed_source):
            print("No source vertex groups match the filter; nothing to do.")
            return {'CANCELLED'}

        for obj_target in objs_selected:
            if obj_target == obj_active:
                continue

            # only operate on mesh objects
            if 'MESH' != obj_target.type:
                print(f"Skipping non-mesh object: {obj_target.name}")
                continue

            vgs_names_target = [vg.name for vg in obj_target.vertex_groups]

            # split target groups into those matching the filter and those that don't
            target_matching = [n for n in vgs_names_target if vg_matches(n)]
            target_nonmatching = [n for n in vgs_names_target if not vg_matches(n)]

            # build final name list
            if True == keep_target_unique:
                # preserve target-unique VGs that match the filter (after processed source VGs)
                final_names = processed_source + [n for n in target_matching if n not in processed_source] + target_nonmatching
            else:
                # remove target-unique matching groups; keep non-matching groups untouched
                final_names = processed_source + target_nonmatching

            if vgs_names_target == final_names:
                print(f"Already matching: {obj_target.name}")
                continue

            mesh = obj_target.data

            # mapping old name -> index for copying weights
            old_name_to_index = {vg.name: idx for idx, vg in enumerate(obj_target.vertex_groups)}

            # create new groups (temporary names) in the desired order and copy weights from old groups when present
            temp_suffix = "__mgtools_new"
            for name in final_names:
                temp_name = name + temp_suffix
                new_vg = obj_target.vertex_groups.new(name=temp_name)

                if name in old_name_to_index:
                    old_idx = old_name_to_index[name]
                    # copy weights vertex-by-vertex
                    for v in mesh.vertices:
                        for g in v.groups:
                            if g.group == old_idx:
                                try:
                                    new_vg.add([v.index], g.weight, 'REPLACE')
                                except Exception:
                                    # ignore possible errors on malformed meshes
                                    pass
                    # copy simple flags if requested
                    if copy_flags:
                        try:
                            old_vg = obj_target.vertex_groups[old_idx]
                            if hasattr(old_vg, 'lock_weight') and hasattr(new_vg, 'lock_weight'):
                                new_vg.lock_weight = old_vg.lock_weight
                        except Exception:
                            pass

            # remove original groups
            for name in list(old_name_to_index.keys()):
                try:
                    vg = obj_target.vertex_groups[name]
                    obj_target.vertex_groups.remove(vg)
                except Exception:
                    pass

            # rename new groups to final names (they are in the desired order)
            for idx, name in enumerate(final_names):
                try:
                    vg = obj_target.vertex_groups[idx]
                    vg.name = name
                except Exception:
                    pass

            print(f"Matched vertex groups for: {obj_target.name}")

        return {'FINISHED'}