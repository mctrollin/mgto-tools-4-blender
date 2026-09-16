import bpy
import bl_math
import colorsys
from mathutils import Matrix # Vector, Euler, 
import bmesh


class MGTOOLS_functions_helper():

    # Selection.Mesh #######################################################
    
    @classmethod
    def get_selected_verts(self, meshobj):
        """Return the selected vertices from a mesh object."""
        return [v for v in meshobj.data.vertices if v.select]

    @classmethod
    def get_selected_vert_indicies(self, meshobj):
        """Return the indices of the selected vertices in a mesh object."""
        selected_verts = self.get_selected_verts(meshobj)
        selected_vert_indices = [v.index for v in selected_verts]
        return selected_vert_indices

    @classmethod
    def get_mirror_axes(self, meshobj):
        """Return the enabled mesh mirror axes as a set of axis names."""
        return {
            axis for axis, enabled in (
                ('X', meshobj.use_mesh_mirror_x),
                ('Y', meshobj.use_mesh_mirror_y),
                ('Z', meshobj.use_mesh_mirror_z),
            ) if enabled
        }

    @classmethod
    def has_mirror_enabled(self, meshobj):
        """Return whether any mesh mirror axis is enabled."""
        return bool(self.get_mirror_axes(meshobj))

    @classmethod
    def get_color_attribute_colors(self, mesh, attribute):
        """Return per-vertex colors from a point or corner color attribute."""
        colors = [(0.0, 0.0, 0.0, 0.0) for _ in mesh.vertices]
        counts = [0 for _ in mesh.vertices]
        if attribute.domain == 'POINT':
            for vertex in mesh.vertices:
                colors[vertex.index] = tuple(attribute.data[vertex.index].color[:])
                counts[vertex.index] = 1
            return colors
        if attribute.domain != 'CORNER':
            return colors
        for loop in mesh.loops:
            vertex_index = loop.vertex_index
            color = attribute.data[loop.index].color
            previous = colors[vertex_index]
            colors[vertex_index] = tuple(previous[channel] + color[channel] for channel in range(4))
            counts[vertex_index] += 1
        for vertex_index, count in enumerate(counts):
            if count > 0:
                colors[vertex_index] = tuple(value / count for value in colors[vertex_index])
        return colors


    # Objects #######################################################

    @classmethod
    def get_children(self, obj, children_list, recursive):
        """Append an object's children to a list, optionally recursively."""
        for child in obj.children:
            children_list.append(child)
            if True == recursive:
                children_list = self.get_children(child, children_list, True)
        return children_list

    @classmethod
    def set_parent(self, child, new_parent, keep_transforms):
        """Set an object's parent while optionally preserving its transforms."""
        if True == keep_transforms:
            if None == new_parent:
                target_matrix = child.matrix_world.copy()
                child.parent = None
                child.matrix_world = target_matrix
            else:
                parent_world_matrix = Matrix.Identity(4) if None == child.parent else child.parent.matrix_world
                target_matrix = new_parent.matrix_world.inverted() @ parent_world_matrix @ child.matrix_parent_inverse
                child.parent = new_parent
                child.matrix_parent_inverse = target_matrix
        else:
            child.parent = new_parent

    @classmethod
    def set_parent_recursive(self, object, new_parent, keep_transforms):
        """Reparent an object and its descendants to a new parent."""
        for child in object.children:
            self.deparent_recursive(child, new_parent)
        self.set_parent(object, new_parent, keep_transforms)

    @classmethod
    def remove_recursive(self, object):       
        """Remove an object and all of its child objects recursively."""
        for child in object.children:
            self.remove_recursive(child)
        bpy.data.objects.remove(object)

    # Mesh #######################################################

    @classmethod
    def get_evaluated_meshdata(self, meshobj):
        """Create and return mesh data evaluated through the dependency graph."""

        # get evaluated data
        depsgraph = bpy.context.evaluated_depsgraph_get()

        # create bmesh clone
        bm = bmesh.new()
        bm.from_object(meshobj, depsgraph)
        meshdata_evaluated = bpy.data.meshes.new(meshobj.name + "get_evaluated_meshdata_bmesh")
        bm.to_mesh(meshdata_evaluated)
        bm.free() # free and prevent further access
        return meshdata_evaluated



    # Modifier #######################################################

    @classmethod
    def get_all_modifier(self, source_object, modifier_type):
        """Return all modifiers of the requested type on an object."""
        modifier = []
        # print("  checking {}".format(source_object))
        for mod in source_object.modifiers:
            # print("    checking {}, {}".format(mod, mod.type))
            # armatures
            if modifier_type == mod.type:
                modifier.append(mod)
        return modifier

    @classmethod
    def transfer_modifier_armature(self, source_objects, target_objects):
        """Transfer the first discovered armature modifier target to objects."""
        print ("transfer_modifier_armature()")
        armature_modifier = []
        armatures = []

        for source_object in source_objects:
            # print("  checking {}".format(source_object))
            for mod in source_object.modifiers:
                # print("    checking {}, {}".format(mod, mod.type))
                # armatures
                if 'ARMATURE' == mod.type:
                    armature_modifier.append(mod)
                    armature = mod.object
                    # print("    found: {}".format(armature))
                    if None != armature and False == (armature in armatures):
                        armatures.append(armature)

        # noting to copy
        if 1 > len(armatures):
            print (" > No armatures found")
            return

        # too much to copy
        if 1 < len(armatures):
            print (" > More then one target Armature detected, only the first ({}) will be used! {}".format(armatures[0], armatures))
            # return

        # target objects shouldn't have an armature modifier applied 
        for target_object in target_objects:
            armature_mod = None

            # Check for existing modifier
            for mod in target_object.modifiers:
                if 'ARMATURE' == mod.type:
                    print (" > Target has already an armature modifier")
                    armature_mod = mod
                    break

            # Add new modifier
            if not armature_mod:
                target_object.modifiers.new(name="Armature", type='ARMATURE')
                armature_mod = target_object.modifiers["Armature"]

            # Set target armature
            armature_mod.object = armatures[0]

    @classmethod
    def bake_shape_keys(self, obj):
        """Bake current shape-key deformation into vertex coordinates and remove shape-keys.

        Assumes `obj` is already selected (and active) and does not modify global selection or mode.
        Uses a context override when calling operators so it doesn't need to change selection.
        """
        try:
            if None == obj or 'MESH' != obj.type:
                return

            # quick exit when no shape keys
            if None == obj.data.shape_keys or 0 >= len(obj.data.shape_keys.key_blocks):
                return

            # Prefer operator that applies the mixed shape-key deformation if supported
            try:
                with bpy.context.temp_override(object=obj):
                    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
            except TypeError:
                # older Blender versions might not support apply_mix; fall back to manual baking

                basis = obj.data.shape_keys.key_blocks[0]
                final_coords = [basis.data[i].co.copy() for i in range(len(obj.data.vertices))]
                for kb in obj.data.shape_keys.key_blocks[1:]:
                    val = kb.value
                    if 0.0 == val:
                        continue
                    for i, kv in enumerate(kb.data):
                        final_coords[i] += (kv.co - basis.data[i].co) * val

                # assign baked coords to the mesh vertices
                for i, v in enumerate(obj.data.vertices):
                    v.co = final_coords[i]

                # remove all shape keys (try all=True first, fall back to iterative removal)
                try:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.shape_key_remove(all=True)
                except Exception:
                    while obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 0:
                        try:
                            with bpy.context.temp_override(object=obj):
                                bpy.ops.object.shape_key_remove()
                        except Exception:
                            break
            except Exception as e:
                # some other error occurred when trying apply_mix; try conservative manual bake as fallback
                try:
                    basis = obj.data.shape_keys.key_blocks[0]
                    final_coords = [basis.data[i].co.copy() for i in range(len(obj.data.vertices))]
                    for kb in obj.data.shape_keys.key_blocks[1:]:
                        val = kb.value
                        if 0.0 == val:
                            continue
                        for i, kv in enumerate(kb.data):
                            final_coords[i] += (kv.co - basis.data[i].co) * val
                    for i, v in enumerate(obj.data.vertices):
                        v.co = final_coords[i]
                except Exception:
                    print("Warning: failed to bake shape keys for {}: {}".format(obj, e))
                # try to remove shape keys anyway
                try:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.shape_key_remove(all=True)
                except Exception:
                    while obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 0:
                        try:
                            with bpy.context.temp_override(object=obj):
                                bpy.ops.object.shape_key_remove()
                        except Exception:
                            break

        except Exception as e:
            print("Warning: failed to bake shape keys for {}: {}".format(obj, e))

    @classmethod
    def apply_modifiers_smartly(self, obj, ignore: str = ""):
        """Apply viewport modifiers and remove modifiers that cannot be applied."""
        # For each modifier
        # Removes obviously broken modifiers (e.g. missing target object) and
        # tries to apply modifiers; if applying fails the modifier is removed.
        #
        # Assumes `obj` is already selected (and active). Uses context overrides
        # for operator calls so it does not modify selection or active object.
        #
        # ignore: optional name prefix (case-sensitive); modifiers whose name starts
        #         with this prefix are skipped entirely (e.g. reserved for shape key baking).

        if None == obj:
            return

        # iterate over a copy because we may remove modifiers during iteration
        for modifier in list(obj.modifiers):
            # skip modifiers reserved for shape key conversion
            if ignore and modifier.name.startswith(ignore):
                continue
            # -------------
            # Custom behaviour for certain modifiers:
            if modifier.type == 'DATA_TRANSFER':
                try:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.datalayout_transfer(modifier=modifier.name)
                except Exception as e:
                    print(f"Warning: data transfer failed for modifier '{modifier.name}' on '{obj.name}': {e}")

            # Try to apply the modifier if it is enabled for viewport
            if modifier.show_viewport:
                try:
                    with bpy.context.temp_override(object=obj):
                        bpy.ops.object.modifier_apply(modifier=modifier.name)
                except Exception as e:
                    # applying failed -> try to remove the modifier to avoid future issues
                    print(f"Warning: applying modifier '{modifier.name}' on '{obj.name}' failed: {e}. Removing modifier.")
                    try:
                        # modifier object may have been invalidated, remove by name if present
                        if modifier.name in obj.modifiers:
                            obj.modifiers.remove(obj.modifiers[modifier.name])
                    except Exception as e2:
                        print(f"Warning: failed to remove broken modifier '{modifier.name}' on '{obj.name}': {e2}")


    # View Layer / Collection #######################################################

    # check all of the top level LayerCollections and recursively all of their child LayerCollections
    @classmethod
    def get_layercollection(self, collection):
        """Find the view-layer collection corresponding to a Blender collection."""
        lc_out = None
        for lc in bpy.context.view_layer.layer_collection.children:
            lc_out = self.get_layercollection_r(lc, collection)
            if None != lc_out:
                return lc_out

    # try find the related LayerCollection to a supplied Collection (recursive)
    @classmethod
    def get_layercollection_r(self, layer_collection, collection):
        """Recursively find a collection beneath a layer collection."""
        # check the supplied LayerCollection
        if layer_collection.collection == collection:
            return layer_collection
        # otherwise, check all of its children
        lc_out = None
        for lc_child in layer_collection.children:
            lc_out = self.get_layercollection_r(lc_child, collection)
            if None != lc_out:
                break
        return lc_out

    @classmethod
    def get_layercollection_path(self, collection, layer_collection=None):
        """Return the LayerCollection path for a collection in the current view layer."""
        if None == layer_collection:
            layer_collection = bpy.context.view_layer.layer_collection
        if layer_collection.collection == collection:
            return [layer_collection]
        for child in layer_collection.children:
            path = self.get_layercollection_path(collection, child)
            if None != path:
                return [layer_collection] + path
        return None

    # Vertex Groups #######################################################

    @classmethod
    def try_get_vgroup(self, meshobj, vgroup_name):
        """Return a named vertex group from a mesh object."""
        return meshobj.data.vertices.groups[vgroup_name]

    # returns all vertex groups which belong to an armature bone
    @classmethod
    def get_bone_vgroups(self, obj, armature):
        """Return vertex groups whose names match bones in an armature."""
        vgroups_bones = []
        if 'ARMATURE' != armature.type:
            return vgroups_bones
        # for every vertex group of the obj
        for vg in obj.vertex_groups:
            # check if there exists a bone with the same name in the supplied armature
            if True == any(bone.name == vg.name for bone in armature.data.bones): # vg.name in armature.bones:
                vgroups_bones.append(vg)
        return vgroups_bones
    
    # returns all vertex groups of a supplied vertex which belong to an armature bone
    @classmethod
    def get_bone_vgelements_from_vert(self, meshobj, vert_idx, armature):
        """Return armature-bone group elements assigned to a mesh vertex."""
        vgroups_bones = []
        # check if meshobj is really a mesh type
        if 'MESH' != meshobj.type:
            return vgroups_bones
        if 'ARMATURE' != armature.type:
            return vgroups_bones
        # check if the vertex index is not out of bounds
        if 0 > vert_idx or len(meshobj.data.vertices) <= vert_idx:
            return vgroups_bones
        # get the relevant vertex
        vert = meshobj.data.vertices[vert_idx]
        # for every vertex group element connected to this vertex
        for vge in vert.groups:
            # get connected vertex group
            if 0 <= vge.group < len(meshobj.vertex_groups):
                vg = meshobj.vertex_groups[vge.group]
                # check if there exists a bone with the same name in the supplied armature
                if True == any(bone.name == vg.name for bone in armature.data.bones): # vg.name in armature.bones:
                    vgroups_bones.append(vge)
                # else:
                #     print ("     vert {} with weight: {} from vg: {} which is not part of the used armature{}".format(vert_idx, vge.weight, vg.name, armature))
        return vgroups_bones

    @classmethod
    def get_bone_vgroups_from_vert(self, meshobj, vert_idx, armature):
        """Return armature-bone vertex groups assigned to a mesh vertex."""
        vgelements = self.get_bone_vgelements_from_vert(meshobj, vert_idx, armature)
        vgroups = []
        for vge in vgelements:
            vgroups.append(meshobj.vertex_groups[vge.group])
        return vgroups

    @classmethod
    def create_vgroups_from_names(self, meshobj, vg_names):
        """Create any named vertex groups that are missing from a mesh object."""
        # check if meshobj is really a mesh type
        if 'MESH' != meshobj.type:
            return
        for vg_name in vg_names:
            # try get vertex group
            vg = meshobj.vertex_groups.get(vg_name)
            # if vertex group does already exist continue with next name
            if None != vg: 
                continue
            # create new vertex group
            vg = meshobj.vertex_groups.new(name=vg_name)

    @classmethod
    def remove_vgroups(self, meshobj, only_unused, include_locked):
        """Remove eligible vertex groups from a mesh object."""
        # check if meshobj is really a mesh type
        if 'MESH' != meshobj.type:
            return

        groups_to_remove = []
        for vg in meshobj.vertex_groups:
            
            # filter locked groups
            if True == vg.lock_weight and False == include_locked:
                continue

            if True == only_unused:
                # check if weights are set for this vg
                has_weights = 0 < self.get_weights_count(meshobj.data, vg)

                # filter vgs to be removed
                if True == has_weights:
                    continue
            
            groups_to_remove.append(vg)

        # Mutating a Blender collection during iteration can skip entries.
        for vg in groups_to_remove:
            print (" > Removing vertex group ({})! ".format(vg.name))
            meshobj.vertex_groups.remove(vg)

    # Armature #######################################################


    # Weighting #######################################################

    # mode can be 'REPLACE', 'ADD' or 'SUBTRACT'
    @classmethod
    def set_weights(self, vgroup, vindices, weight:float, mode):
        """Assign a weight to vertex indices using the requested blend mode."""
        vgroup.add(vindices, weight, mode)

    # mode can be 'REPLACE', 'ADD' or 'SUBTRACT'
    @classmethod
    def lerp_weights(self, vgroup, vindices, weight:float, factor:float, mode):
        """Interpolate existing weights toward a target weight."""
        for idx in vindices:
            # this 'try' is stupid but I don't want to make a mesh input a requirement here
            weight_from = 0
            try:
                weight_from = vgroup.weight(idx)
            except:
                pass
            weight_lerped = bl_math.lerp(weight_from, weight, factor)
            vgroup.add([idx], weight_lerped, mode)

    # returns (for a given mesh and a given vertex group) a list with the weight of every vertice
    # Note: it will return a weight of 0 even if the vertex is not part of the vertex group
    @classmethod
    def get_weights_from_selection(self, mesh, vgroup, vindices):
        """Return vertex-group weights for the supplied vertex indices."""
        weights = [0] * len(mesh.vertices)
        group_index = vgroup.index
        for vidx in vindices:
            v = mesh.vertices[vidx]
            for vge in v.groups:
                if vge.group != group_index:
                    continue           
                weights[vidx] = vge.weight
                break
        return weights

    @classmethod
    def get_weights(self, mesh, vgroup):
        """Return the weight of every mesh vertex in a vertex group."""
        weights = [0] * len(mesh.vertices)
        group_index = vgroup.index
        for v in mesh.vertices:
            for vge in v.groups:
                if vge.group != group_index:
                    continue           
                weights[v.index] = vge.weight
                break
        return weights

    # returns the average weight of all supplied vertices within the given vertex group
    @classmethod
    def get_weight_average(self, meshobj, vgroupidx, vindices):
        """Return the average vertex-group weight across supplied indices."""
        weight_average = 0
        selected_vert_indices = vindices
        selected_verts_count = len(selected_vert_indices)
        # if nothing is selected just exit
        if 0 >= selected_verts_count:
            return weight_average

        # get weights
        # weights = list(range(0,len(meshobj.data.vertices)))
        weights = MGTOOLS_functions_helper.get_weights_from_selection(meshobj.data, meshobj.vertex_groups[vgroupidx], selected_vert_indices)
        
        # accumulate weights
        weight_accum = 0
        for idx in selected_vert_indices:
            weight_accum += weights[idx]

        # calculate average
        weight_average = weight_accum / selected_verts_count
        return weight_average

    # returns the number of vertices which are part of this vertex group
    @classmethod
    def get_weights_count(self, mesh, vgroup):
        """Return the number of mesh vertices assigned to a vertex group."""
        weights = 0
        group_index = vgroup.index
        for vidx in range(len(mesh.vertices)):
            v = mesh.vertices[vidx]
            for vge in v.groups:
                if vge.group != group_index:
                    continue           
                weights += 1
                break
        return weights

    @classmethod
    def apply_modifier_as_shape_key(self, obj, modifier_name):
        """Apply a single modifier as a shape key using its current name.

        The resulting shape key will inherit the modifier's current name.
        Requires obj to be the active object in Object Mode.
        Logs a warning and skips if the modifier cannot be applied as a shape key.

        Args:
            obj:           A Blender mesh object (must be active).
            modifier_name: Current name of the modifier on obj.
        """
        if modifier_name not in obj.modifiers:
            print(f"Warning: modifier '{modifier_name}' not found on '{obj.name}', skipping.")
            return
        try:
            with bpy.context.temp_override(object=obj):
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=modifier_name)
        except Exception as e:
            print(f"Warning: modifier '{modifier_name}' on '{obj.name}' cannot be applied as shape key, skipping: {e}")

    @classmethod
    def apply_prefixed_modifier_as_shape_key(self, obj, modifier_name, prefix):
        """Strip prefix from a modifier's name, rename it, then apply it as a shape key.

        Renames the modifier to the stripped name before applying so the resulting shape key
        gets the correct name. On failure the original name is restored.

        Args:
            obj:           A Blender mesh object (must be active).
            modifier_name: Current name of the modifier on obj (must start with prefix).
            prefix:        Prefix to strip from modifier_name to produce the shape key name.
        """
        if modifier_name not in obj.modifiers:
            print(f"Warning: modifier '{modifier_name}' not found on '{obj.name}', skipping.")
            return
        stripped_name = modifier_name[len(prefix):]
        mod = obj.modifiers[modifier_name]
        mod.name = stripped_name
        try:
            self.apply_modifier_as_shape_key(obj, stripped_name)
        except Exception as e:
            print(f"Warning: prefix-apply failed for '{stripped_name}' on '{obj.name}': {e}")
            # restore original name so apply_modifiers_smartly can handle it
            if stripped_name in obj.modifiers:
                obj.modifiers[stripped_name].name = modifier_name

    @classmethod
    def apply_prefixed_modifiers_as_shape_keys(self, obj, prefix):
        """Apply all modifiers whose name starts with prefix as shape keys, stripping the prefix.

        Iterates a snapshot of the modifier list so mutations during iteration are safe.
        Skips the feature entirely when prefix is empty.

        Args:
            obj:    A Blender mesh object (must be active).
            prefix: Case-sensitive name prefix to match and strip.
        """
        if not prefix or 'MESH' != obj.type:
            return
        prefix_lower = prefix.lower()
        # snapshot names to avoid mutation issues during iteration
        matching = [
            mod.name for mod in obj.modifiers
            if mod.name.lower().startswith(prefix_lower)
        ]
        for mod_name in matching:
            stripped = mod_name[len(prefix):]
            print(f" > applying modifier '{mod_name}' as shape key '{stripped}' on '{obj.name}'")
            self.apply_prefixed_modifier_as_shape_key(obj, mod_name, prefix)

    @classmethod
    def remove_lowest_weights(self, meshobj, armature, max_influences):
        """Remove bone influences exceeding max_influences per vertex, keeping the strongest ones.

        Automatically scopes to selected vertices if any are selected in the mesh data;
        otherwise processes all vertices. When exactly one vertex is selected, any vertex
        groups that were filtered out by get_bone_vgelements_from_vert (i.e. not matching
        a bone in the supplied armature) are logged to the console.

        Args:
            meshobj:        A Blender mesh object to process.
            armature:       The armature object whose bones define valid vertex groups.
            max_influences: Maximum number of bone influences allowed per vertex.
        """
        print("remove_lowest_weights()")

        # check if meshobj is really a mesh type
        if not meshobj or 'MESH' != meshobj.type:
            return
        if not armature or 'ARMATURE' != armature.type:
            return

        # determine vertex scope: selected vertices only, or all
        selected_indices = self.get_selected_vert_indicies(meshobj)
        selected_set = set(selected_indices) if selected_indices else None
        log_filtered = selected_set is not None and 1 == len(selected_set)

        if selected_set is not None:
            print(" > selection mode: {} vertices".format(len(selected_set)))
        else:
            print(" > full mesh mode")

        # for every vertex
        for i, vert in enumerate(meshobj.data.vertices):

            # skip unselected vertices when a selection is active
            if selected_set is not None and i not in selected_set:
                continue

            # get only vertex groups elements which belong to a bone
            vert_vges = self.get_bone_vgelements_from_vert(meshobj, i, armature)

            # when exactly one vertex is selected, log groups filtered out by get_bone_vgelements_from_vert
            if log_filtered:
                bone_vge_group_indices = {vge.group for vge in vert_vges}
                for vge in vert.groups:
                    if vge.group not in bone_vge_group_indices:
                        vg_name = meshobj.vertex_groups[vge.group].name if 0 <= vge.group < len(meshobj.vertex_groups) else "<unknown>"
                        print(" > vert {}: vg '{}' (w={:.3f}) skipped (no matching bone)".format(i, vg_name, vge.weight))

            # continue if this vertex doesn't use more influences then allowed
            if max_influences >= len(vert_vges):
                continue

            # sort vertex groups by influence value
            vert_vges.sort(key=lambda x: x.weight, reverse=True)

            # resize to maximum allowed amount of influences
            vgroups_keep = vert_vges[:max_influences]

            # remove weights
            for vge in vert_vges:
                if 0 > vge.group:
                    continue
                if vge.group >= len(meshobj.vertex_groups):
                    print("Strange vertex group found - skipping: " + vge.group)
                    continue
                if vge in vgroups_keep:
                    continue
                # get vertex group
                vg = meshobj.vertex_groups[vge.group]
                # remove vertex from group
                vg.remove([i])
                # print ("    removing vert {} with weight: {} from vg: {}".format(i, vge.weight, vg.name))

    @classmethod
    def remove_weights_below_threshold(self, meshobj, armature, threshold):
        """Remove bone influences below threshold per vertex.

        Automatically scopes to selected vertices if any are selected in the mesh data;
        otherwise processes all vertices. When exactly one vertex is selected, any vertex
        groups that were filtered out by get_bone_vgelements_from_vert (i.e. not matching
        a bone in the supplied armature) are logged to the console.

        Args:
            meshobj:   A Blender mesh object to process.
            armature:  The armature object whose bones define valid vertex groups.
            threshold: Minimum weight value to keep; influences strictly below this are removed.
        """
        print("remove_weights_below_threshold()")

        # check if meshobj is really a mesh type
        if not meshobj or 'MESH' != meshobj.type:
            return
        if not armature or 'ARMATURE' != armature.type:
            return

        # determine vertex scope: selected vertices only, or all
        selected_indices = self.get_selected_vert_indicies(meshobj)
        selected_set = set(selected_indices) if selected_indices else None
        log_filtered = selected_set is not None and 1 == len(selected_set)

        if selected_set is not None:
            print(" > selection mode: {} vertices".format(len(selected_set)))
        else:
            print(" > full mesh mode")

        # for every vertex
        for i, vert in enumerate(meshobj.data.vertices):

            # skip unselected vertices when a selection is active
            if selected_set is not None and i not in selected_set:
                continue

            # get only vertex groups elements which belong to a bone
            vert_vges = self.get_bone_vgelements_from_vert(meshobj, i, armature)

            # when exactly one vertex is selected, log groups filtered out by get_bone_vgelements_from_vert
            if log_filtered:
                bone_vge_group_indices = {vge.group for vge in vert_vges}
                for vge in vert.groups:
                    if vge.group not in bone_vge_group_indices:
                        vg_name = meshobj.vertex_groups[vge.group].name if 0 <= vge.group < len(meshobj.vertex_groups) else "<unknown>"
                        print(" > vert {}: vg '{}' (w={:.3f}) skipped (no matching bone)".format(i, vg_name, vge.weight))

            # for every bone influence on this vertex...
            for vge in vert_vges:
                # if at or above threshold keep it
                if threshold <= vge.weight:
                    continue
                # get vertex group
                vg = meshobj.vertex_groups[vge.group]
                # remove vertex from group
                vg.remove([i])


    # Animations #######################################################

    # Retrieve all actions given a blender object. Includes NLA-actions
    @classmethod
    def get_all_actions(self, obj):
        """Return an object's active action and actions used by NLA strips."""
        actions = []
        if None == obj or None == obj.animation_data: 
            return actions
        # active action
        if obj.animation_data.action:
            actions.append(obj.animation_data.action)
        # for every nla-track
        for track in obj.animation_data.nla_tracks:
            # for every strip 
            for strip in track.strips:
                # the associated action
                actions.append(strip.action)
        return actions

    @classmethod
    def get_all_animstrips(self, obj):
        """Return all animation strips from an object's NLA tracks."""
        strips = []
        if None == obj or None == obj.animation_data: 
            return strips
        # for every nla-track
        for track in obj.animation_data.nla_tracks:
            # for every strip 
            for strip in track.strips:
                strips.append(strip)
        return strips

    @classmethod
    def copy_animation_data(self, obj_from, obj_to):
        """Copy NLA track and strip settings from one object to another."""
        
        #print ("copy_animation_data()")

        sourceObj = obj_from
        targetObj = obj_to

        # get and check source animation data
        source_anim_data = sourceObj.animation_data
        if None == source_anim_data:
            return

        # clear animation data from target
        if targetObj.animation_data is not None:
            targetObj.animation_data_clear()

        # create animation data on target
        targetObj.animation_data_create()   
        
        target_anim_data = targetObj.animation_data

        # copy animation data
        for source_nla_track in source_anim_data.nla_tracks:
            # create tracks
            target_nla_track = target_anim_data.nla_tracks.new()
            target_nla_track.name = source_nla_track.name
            for source_strip in source_nla_track.strips:
                #create strips
                # NOTE: Blender's NlaStrips.new expects an integer start frame in some versions
                target_strip = target_nla_track.strips.new(source_strip.name, int(source_strip.frame_start), source_strip.action)
                # new() sometimes ignores the supplied name, so set it explicitly
                target_strip.name = source_strip.name
                target_strip.blend_in = source_strip.blend_in
                target_strip.blend_out = source_strip.blend_out
                target_strip.blend_type = source_strip.blend_type
                target_strip.extrapolation = source_strip.extrapolation
                target_strip.frame_start = source_strip.frame_start
                target_strip.frame_end = source_strip.frame_end
                target_strip.influence = source_strip.influence
                target_strip.mute = source_strip.mute
                target_strip.repeat = source_strip.repeat
                target_strip.strip_time = source_strip.strip_time
                target_strip.use_animated_influence = source_strip.use_animated_influence
                target_strip.use_animated_time_cyclic = source_strip.use_animated_time_cyclic
                target_strip.use_auto_blend = source_strip.use_auto_blend
                target_strip.use_reverse = source_strip.use_reverse
                target_strip.use_sync_length = source_strip.use_sync_length


    # Misc #######################################################

    @classmethod
    def convert_weight_2_color(self, value):
        """Convert a normalized vertex weight to a display color."""
        col = (0,0,0,0)
        # special case: weight = 0
        if 0 >= value and 'ACTIVE' == bpy.context.scene.tool_settings.vertex_group_user:
            return col
        # get color
        if True == bpy.context.preferences.view.use_weight_color_range:
            c = bpy.context.preferences.view.weight_color_range.evaluate(value)
            col = (c[0], c[1], c[2], c[3])
        else:
            hue = 2 * (1 - value) / 3
            tmprgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            col = (tmprgb[0], tmprgb[1], tmprgb[2], 1)
        return col


    # Transform #######################################################

    @classmethod
    def get_local_location(self, obj):
        """Return an object's location transformed into local parent space."""
        # transform intrinsic- to local-space
        if None == obj:
            return (0, 0, 0)
        if None == obj.parent:
            return obj.location
        ao_pos_i = obj.location
        ao_pos_l = (obj.matrix_parent_inverse @ ao_pos_i)
        return ao_pos_l
    
    @classmethod
    def get_world_location(self, obj):
        """Return an object's location transformed into world space."""
        # transform intrinsic- to world-space
        if None == obj:
            return (0, 0, 0)
        if None == obj.parent:
            return obj.location
        ao_pos_i = obj.location
        ao_pos_l = obj.matrix_parent_inverse @ ao_pos_i
        ao_pos_w = obj.parent.matrix_world @ ao_pos_l
        return ao_pos_w


    # Debug.Print #######################################################

    @classmethod
    def print_collection(self, collection):
        """Print each item in a collection to the console."""
        for c in collection:
            print(c)
