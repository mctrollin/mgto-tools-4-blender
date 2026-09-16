import bpy
import mathutils
from mathutils import Vector, Euler, Matrix
import uuid
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . import mgtools_functions_log

class MGTOOLS_functions_macros():


    # Object.Selection #######################################################

    @classmethod
    def get_first_selected_mesh(self):
        """Return the first selected mesh object, if one exists."""
        for tmpObj in bpy.context.selected_objects:
            if 'MESH' == tmpObj.type:
                return tmpObj

    @classmethod
    def get_first_selected_armature(self):
        """Return the first selected armature object, if one exists."""
        for tmpObj in bpy.context.selected_objects:
            if 'ARMATURE' == tmpObj.type:
                return tmpObj
            else:
                print ("{} is {}".format(tmpObj, tmpObj.type))

    @classmethod
    def get_armature_from_first_selected_mesh(self):
        """Return the armature targeted by the first selected mesh modifier."""
        mesh_object = self.get_first_selected_mesh()
        if None == mesh_object:
            return

        # process modifiers
        for mod in mesh_object.modifiers:
            # armatures
            if 'ARMATURE' == mod.type:
                # auto select armatures
                return mod.object

    @classmethod
    def select_only(self, refobj):
        """Select one object and make it the active object."""
        if None == refobj:
            return
        if type(refobj) == list:
            print("Warning: input should be one object but its:{}".format(len(refobj)))
            return
        self.select_objects(refobj, True)

    @classmethod
    def select_objects(self, ref_objects, set_active:bool=False):
        """Select the supplied objects and optionally make the first active."""
        try:
            len(ref_objects)
        except TypeError:
            ref_objects = [ref_objects]

        if None == ref_objects or 0 >= len(ref_objects):
            return

        # clear selection
        for obj in bpy.data.objects:
            if None == obj: continue
            obj.select_set(False)

        # select only our mesh object
        for obj in ref_objects:
            if None == obj: continue
            obj.select_set(True)

        # set active object
        if True == set_active:
            bpy.context.view_layer.objects.active = ref_objects[0]

    @classmethod
    def cache_selection_state(self):
        """Return copies of the current selection and active object."""
        return (bpy.context.selected_objects.copy(),
                bpy.context.view_layer.objects.active)

    @classmethod
    def restore_selection_state(self, cached_selection, cached_active):
        """Restore a previously cached selection and active object."""
        self.select_objects(cached_selection, False)
        bpy.context.view_layer.objects.active = cached_active


    # Object.Misc #######################################################

    # Duplicate selected objects and move them into a newly created collection
    @classmethod
    def duplicate_to_collection(self, source_objects, select_clones):
        """Duplicate objects into a temporary collection and optionally select the clones."""
        
        # cache current selection
        cached_selection, cached_active = self.cache_selection_state()

        # set selection
        self.select_objects(source_objects, True)
        
        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting object for duplication: {}".format(source_objects))
            return

        # --------------------------------------------

        # create a copy of all selected objects and select them
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')

        # create a temporary collection for exporting purposes
        tmp_export_collection = bpy.data.collections.new("TmpExport_" + str(uuid.uuid4().hex))
        bpy.context.scene.collection.children.link(tmp_export_collection)

        # move duplicates to new collection
        for obj in bpy.context.selected_objects:
            for col in obj.users_collection: # unlink from existing collection(s)
                col.objects.unlink(obj)
            tmp_export_collection.objects.link(obj) # link to our new collection

        # --------------------------------------------

        # option: revert selection or not
        # print(" > set selection")
        if False == select_clones:
            self.restore_selection_state(cached_selection, cached_active)
        else:
            # select the newly created clones (they are in the tmp collection)
            self.select_objects(list(tmp_export_collection.objects), True)

        return tmp_export_collection

    # De-instanciate a collection instance and remove the parent null objects
    @classmethod
    def make_collection_instance_real(self, collection_instance):
        """Make a collection instance real, preserve its hierarchy, and remove its root."""

        if None == collection_instance:
            return

        if None == collection_instance.instance_collection:
            return

        # cache current selection
        cached_selection, cached_active = self.cache_selection_state()

        # --------------------------------------------

        # set selection
        MGTOOLS_functions_macros.select_only(collection_instance)

        # keep parent and hierarchy, we only want to get rid of the instance-state for now
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)

        # make single user (as data block is still shared with the object from the instanzed collection)
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, animation=False)

        # get children
        childs = []
        childs.extend(collection_instance.children)
        childs_all = MGTOOLS_functions_helper.get_children(collection_instance, [], True)

        # remove all childs from the instance root dummy
        for child in collection_instance.children:
            MGTOOLS_functions_helper.set_parent(child, collection_instance.parent, True) # child.parent = collection_instance.parent

        # modify cached selection
        if collection_instance in cached_selection:
            cached_selection.remove(collection_instance)
        if collection_instance is cached_active:
            cached_active = None

        # remove the root dummy
        bpy.data.objects.remove(collection_instance)
        # bpy.ops.object.delete({"selected_objects": [collection_instance]})

        # --------------------------------------------

        # option: revert selection or not
        # print(" > set selection")
        # if False == select_clones:
        self.restore_selection_state(cached_selection, cached_active)
        # else:
        #     self.select_objects(clones_meshes, True)

        return childs_all


    # Object.Manipulation #######################################################

    @classmethod
    def make_snapshot_from(self, source_objects_raw, merge_clones, prefix, postfix, select_clones, type_filter, modifier_to_shapekey_prefix: str = ""):
        """Duplicate, process, and optionally merge source objects into a snapshot."""
        
        clones = []

        if None == source_objects_raw or 0 >= len(source_objects_raw):
            return clones

        # prepare source objects list
        source_objects = []
        if None != type_filter and 0 < len(type_filter):
            for source_object in source_objects_raw:
                if type_filter == source_object.type:
                    source_objects.append(source_object)
            if 0 >= len(source_objects):
                return clones
        else:
            source_objects = source_objects_raw

        # print ("Create snapshot:")

        # cache current selection
        cached_selection, cached_active = self.cache_selection_state()
        
        # create clones
        clones_other = []
        clones_meshes = []
        
        # --------------------------------------------

        # set selection
        self.select_objects(source_objects, True)

        # Impportant! source_objects and clones array might not be ordered the same way!
        # Therefore we create a new source_objects array from the current selection
        # This one will have the same order as the clones array!
        source_objects_cached = bpy.context.selected_objects.copy()

        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting object for duplication: {}".format(source_objects))
            return clones

        # create a copy of all selected objects and select these
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')

        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting clone of: {}".format(source_object))
            return clones

        clones = bpy.context.selected_objects.copy()

        num_meshes = 0
        for idx, clone in enumerate(clones):
            if 'MESH' == clone.type:
                num_meshes += 1
        
        # Check if we have to process a mesh-merge operation
        merge = merge_clones and num_meshes > 1

        print(" > processing duplicates: {}".format(clones))
        for idx, clone in enumerate(clones):
            
            self.select_only(clone)
            source_object = source_objects_cached[idx]

            # add name pre- and postfix
            if 0 < len(prefix) or 0 < len(postfix):
                new_name = source_object.name

                if 0 < len(prefix): 
                    new_name = prefix + new_name

                if 0 < len(postfix):
                    new_name = new_name + postfix

                clone.name = new_name

            # make library linked data-blocks local to this file
            bpy.ops.object.make_local(type='SELECT_OBDATA')
            # make linked data local to each object
            bpy.ops.object.make_single_user(
                type='SELECTED_OBJECTS', 
                object=True, 
                obdata=True, 
                material=False, 
                animation=False, 
                #obdata_animation=False
                )

            # mesh specific processing
            if 'MESH' == clone.type:
                if True == merge:
                    # For now we can't merge shape keys so we always apply them. 
                    # TODO: add option to merge or apply shape keys
                    # bake shape keys first (deform verts and remove shape keys)
                    MGTOOLS_functions_helper.bake_shape_keys(clone)

                # Apply all modifiers except those reserved for shape key conversion
                # If some modifiers are required (e.g. Armature) they need to be re-applied afterwards
                MGTOOLS_functions_helper.apply_modifiers_smartly(obj=clone, ignore=modifier_to_shapekey_prefix)

                # Apply prefixed modifiers as shape keys after all other modifiers are done
                # (mesh has no shape keys at this point, so prefixed modifiers can be applied cleanly)
                if modifier_to_shapekey_prefix:
                    MGTOOLS_functions_helper.apply_prefixed_modifiers_as_shape_keys(clone, modifier_to_shapekey_prefix)

                # Double check that the merged object is a mesh
                if True == merge:
                    bpy.ops.object.convert(target='MESH')

                # add to mesh list
                clones_meshes.append(clone)
            else:
                clones_other.append(clone)

        # --------------------------------------------
        
        # by doing one object after the other we have more control over the process - problem: this won't retain the correct hierarchy
        # print(" > duplicating objects: {}".format(source_objects))
        # for source_object in source_objects:
            
        #     # set selection
        #     self.select_only(source_object)

        #     if 0 >= len(bpy.context.selected_objects):
        #         print("Problem selecting object for duplication: {}".format(source_object))
        #         continue

        #     # create a copy of the selected object(s) and select it/them
        #     bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')

        #     if 0 >= len(bpy.context.selected_objects):
        #         print("Problem selecting clone of: {}".format(source_object))
        #         continue

        #     # get and store clone
        #     clone = bpy.context.selected_objects[0]

        #     # add name prefix
        #     if 0 < len(prefix): 
        #         clone.name = prefix + source_object.name            

        #     # mesh specific processing
        #     if 'MESH' == source_object.type:
        #         # apply all modifiers
        #         bpy.ops.object.convert(target='MESH')
        #         # add to mesh list
        #         clones_meshes.append(clone)
        #     else:
        #         clones_other.append(clone)

        # --------------------------------------------

        # print (" > source_objects: {}".format(source_objects))
        # print (" > clones_other: {}".format(clones_other))
        # print (" > clones_meshes: {}".format(clones_meshes))
        
        
        # self.select_objects(clones_meshes, True)
        bpy.ops.object.select_all(action='DESELECT')

        # option: join clones_meshes
        clones_meshes_joined = []
        if True == merge and 1 < len(clones_meshes):
            clones_meshes_to_join = []
            clones_meshes_to_join.extend(clones_meshes)               
            
            print(" > joining objects: {}".format(clones_meshes_to_join))
            for clone_mesh_to_join in clones_meshes_to_join:
                clones_meshes.remove(clone_mesh_to_join)

            # join
            # ctx = bpy.context.copy() # does not work
            # ctx['selected_objects'] = clones_meshes_to_join
            # bpy.ops.object.join(ctx)
            self.select_objects(clones_meshes_to_join, True) # select clones for further processing with bpy.ops
            bpy.ops.object.join()

            clones_meshes_joined = bpy.context.selected_objects
            # for clone_mesh_joined in clones_meshes_joined:
            #     clone_mesh_joined.name += "_joinedSnapshot" # this name can and will be used to filtering later

        # get list of all final clones
        clones = clones_other + clones_meshes + clones_meshes_joined

        # option: revert selection or not
        # print(" > set selection")
        if False == select_clones:
            self.restore_selection_state(cached_selection, cached_active)
        else:
            self.select_objects(clones_meshes, True)

        return clones

    @classmethod
    def set_pivot(self, target_objects, new_loc=(0,0,0), new_rot_euler=(0,0,0), new_scale=(1,1,1), apply_scale=False):
        """Set object origins and transforms around a temporary cursor pivot."""
        # checks
        if None == target_objects or 0 >= len(target_objects):
            return
        
        # Prepare -------------------------------------------
        # de-link values so we don't alter the original ones
        new_loc = new_loc.copy()
        new_rot_euler = new_rot_euler.copy()

        # Cache cursor transforms
        cursor_location_cached = bpy.context.scene.cursor.location
        cursor_rotation_cached = bpy.context.scene.cursor.rotation_euler

        # Cache selection
        selected_objects_cached, active_object_cached = self.cache_selection_state()

        # Change cursor's transforms
        bpy.context.scene.cursor.location = new_loc
        bpy.context.scene.cursor.rotation_euler = new_rot_euler
 
        # Set selection
        bpy.context.view_layer.objects.active = None
        self.select_objects(target_objects, False)

        # Cache and clear parents -------------------------------------------
        parents_cache = list(range(len(target_objects)))
        for i, target_object in enumerate(target_objects):
            parents_cache[i] = target_object.parent
            # un-parent
            MGTOOLS_functions_helper.set_parent(child=target_object, new_parent=None, keep_transforms=True)

        # Scale -------------------------------------------
        for obj in target_objects:
            # apply inverse target scale (object will be smaller) and apply scale (scale will be 1)
            obj.scale = obj.scale * mathutils.Vector((1.0/new_scale[0], 1.0/new_scale[1], 1.0/new_scale[2]))
            self.select_objects(obj, False)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            # now apply target scale (object gets old size but pivot has new scale)
            obj.scale = new_scale

        # Position -------------------------------------------
        # Set origin location to cursor location
        self.select_objects(target_objects, False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Rotation -------------------------------------------
        new_rot_mat = new_rot_euler.to_matrix()
        # new_rot_mat_twice = new_rot_mat @ new_rot_mat
        # new_rot_euler_twice_inverted = new_rot_mat_twice.inverted().to_euler()

        for obj in target_objects:
            # set selection for the following ops
            self.select_objects(obj, False)
            # the below works only if the object has not rotation transforms
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            # rotate in inverse target rotation
            obj.rotation_euler = new_rot_mat.inverted().to_euler()
            # apply rotation
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            # rotate back
            obj.rotation_euler = ( new_rot_mat).to_euler()
       
        # Reset parents -------------------------------------------
        for i, target_object in enumerate(target_objects):
            # re-parent (if there wasn't a parent we have to skip or it would reset any transforms!)
            if None != parents_cache[i]:
                MGTOOLS_functions_helper.set_parent(child=target_object, new_parent=parents_cache[i], keep_transforms=True)

        # Cleanup -------------------------------------------
        # Reset cursor
        bpy.context.scene.cursor.location = cursor_location_cached
        bpy.context.scene.cursor.rotation_euler = cursor_rotation_cached

        # Reset selection
        self.restore_selection_state(selected_objects_cached, active_object_cached)

    @classmethod
    def zero_pivot_to(self, target_objects, location):
        """Move object origins to a location and apply their resulting transforms."""
        # Prepare -------------------------------------------
        # Cache cursor transforms
        location_cached = bpy.context.scene.cursor.location

        # Cache selection
        selected_objects_cached, active_object_cached = self.cache_selection_state()

        # Change cursor's transforms
        bpy.context.scene.cursor.location = location

        # Set selection
        bpy.context.view_layer.objects.active = None
        self.select_objects(target_objects, False)

        # Position -------------------------------------------
        # Set origin location to cursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Transforms -------------------------------------------
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=False)

        # Cleanup -------------------------------------------
        # Reset cursor
        bpy.context.scene.cursor.location = location_cached

        # Reset selection
        self.restore_selection_state(selected_objects_cached, active_object_cached)


    # Modifier #######################################################


    # Armature #######################################################


    # Weighting #######################################################

    @classmethod
    def rebuild_active_vertex_group_to(self, position: str, meshobj=None):
        """Rebuild vertex groups with the active group at the top or bottom.

        This data-API alternative avoids repeatedly evaluating the modifier
        stack for each single-position move. Vertex-group weights and the
        supported group properties are copied to a newly ordered collection.
        """
        if meshobj is None:
            meshobj = bpy.context.view_layer.objects.active
        if meshobj is None or meshobj.type != 'MESH':
            return False
        if position not in {'TOP', 'BOTTOM'}:
            return False

        vertex_groups = meshobj.vertex_groups
        if len(vertex_groups) == 0 or vertex_groups.active is None:
            return False
        if meshobj.library is not None or meshobj.override_library is None and meshobj.data.library is not None:
            return False

        group_records = [
            {
                'name': group.name,
                'lock_weight': group.lock_weight,
                'weights': {},
            }
            for group in vertex_groups
        ]
        active_group_name = vertex_groups.active.name

        for vertex in meshobj.data.vertices:
            for element in vertex.groups:
                if 0 <= element.group < len(group_records):
                    group_records[element.group]['weights'].setdefault(element.weight, []).append(vertex.index)

        active_record = next(record for record in group_records if record['name'] == active_group_name)
        remaining_records = [record for record in group_records if record is not active_record]
        if position == 'TOP':
            ordered_records = [active_record] + remaining_records
        else:
            ordered_records = remaining_records + [active_record]

        modifiers_cached = [modifier.show_viewport for modifier in meshobj.modifiers]
        active_object_cached = bpy.context.view_layer.objects.active
        selection_cached = list(bpy.context.selected_objects)
        success = False

        try:
            # Prevent expensive modifier evaluation between each collection
            # removal/addition. The original visibility state is restored.
            for modifier in meshobj.modifiers:
                modifier.show_viewport = False

            while len(vertex_groups) > 0:
                vertex_groups.remove(vertex_groups[0])

            for record in ordered_records:
                group = vertex_groups.new(name=record['name'])
                group.lock_weight = record['lock_weight']
                for weight, indices in record['weights'].items():
                    group.add(indices, weight, 'REPLACE')

            vertex_groups.active_index = next(
                index for index, record in enumerate(ordered_records)
                if record is active_record
            )
            success = True
        except Exception as exc:
            print("Warning: could not rebuild vertex groups: {}".format(exc))
        finally:
            for modifier, show_viewport in zip(meshobj.modifiers, modifiers_cached):
                modifier.show_viewport = show_viewport
            bpy.context.view_layer.objects.active = active_object_cached
            selected_objects = set(selection_cached)
            for obj in bpy.context.view_layer.objects:
                obj.select_set(obj in selected_objects)

        return success

    @classmethod
    def weight_set_vertices(self, meshobj, values):
        """Set active-group weights through Blender's weight-paint operator.

        ``values`` maps vertex indices to final weights. Using the operator,
        rather than VertexGroup.add(), makes Blender's mesh symmetry settings
        apply to each assignment. Vertices with the same target weight are
        assigned together to reduce operator and selection overhead.
        """
        if None == meshobj or 'MESH' != meshobj.type:
            return False
        mode_cached = meshobj.mode
        try:
            if mode_cached != 'WEIGHT_PAINT':
                if mode_cached != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        except RuntimeError as exc:
            print("Warning: could not enter Weight Paint mode for mirrored weight edits: {}".format(exc))
            return False

        ups = bpy.context.scene.tool_settings.weight_paint.unified_paint_settings
        mesh = meshobj.data
        selection_cached = [vert.select for vert in mesh.vertices]
        active_group_cached = meshobj.vertex_groups.active_index
        unified_weight_cached = ups.weight

        with mgtools_functions_log.log_timing("weighting.weight_set_vertices"):
            try:
                # Keep the operator-driven mirror behavior, but batch assignments
                # which use the same weight. This is especially effective for the
                # fixed-weight operations, where all vertices share one value.
                values_by_weight = {}
                for index, value in values.items():
                    if index < 0 or index >= len(mesh.vertices):
                        continue
                    clamped_value = max(0.0, min(1.0, value))
                    values_by_weight.setdefault(clamped_value, []).append(index)

                if values_by_weight:
                    # A single bulk clear replaces the old full-mesh clear for
                    # every individual assignment. Subsequent batches only need
                    # to update the vertices whose temporary selection changes.
                    mesh.vertices.foreach_set('select', [False] * len(mesh.vertices))
                    previous_indices = []
                    for value, indices in values_by_weight.items():
                        for index in previous_indices:
                            mesh.vertices[index].select = False
                        for index in indices:
                            mesh.vertices[index].select = True
                        ups.weight = value
                        bpy.ops.paint.weight_set()
                        previous_indices = indices
            except Exception as exc:
                print("Warning: weight assignment failed: {}".format(exc))
                return False
            finally:
                meshobj.vertex_groups.active_index = active_group_cached
                ups.weight = unified_weight_cached
                mesh.vertices.foreach_set('select', selection_cached)
                if meshobj.mode != mode_cached:
                    try:
                        if mode_cached != 'OBJECT' and meshobj.mode != 'OBJECT':
                            bpy.ops.object.mode_set(mode='OBJECT')
                        if mode_cached != 'OBJECT':
                            bpy.ops.object.mode_set(mode=mode_cached)
                    except RuntimeError as exc:
                        print("Warning: could not restore mesh mode after mirrored weight edit: {}".format(exc))

        return True

    # mode can be 'REPLACE', 'ADD' or 'SUBTRACT'
    @classmethod
    def set_weights_to_selected_mesh(self, weight:float, mode:str, normalize:bool=False):
        """Apply a weight operation to selected vertices in the active mesh group."""
        # get mesh object
        meshobj = bpy.context.view_layer.objects.active
        if None == meshobj or 'MESH' != meshobj.type:
            print("Not a mesh")
            return False

        # get vertex group
        activeVG = meshobj.vertex_groups.active
        if None == activeVG:
            print("No active vertex group")
            return False

        # get selected vertices
        selected_vert_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)

        mirror_enabled = MGTOOLS_functions_helper.has_mirror_enabled(meshobj)

        if mirror_enabled:
            values = {}
            for index in selected_vert_indices:
                if mode == 'REPLACE':
                    target_weight = weight
                else:
                    current_weight = 0.0
                    try:
                        current_weight = activeVG.weight(index)
                    except Exception:
                        pass
                    if mode == 'ADD':
                        target_weight = current_weight + weight
                    else:
                        target_weight = current_weight - weight
                values[index] = target_weight
            if not self.weight_set_vertices(meshobj, values):
                return False
        else:
            MGTOOLS_functions_helper.set_weights(activeVG, selected_vert_indices, weight, mode)

        # normalize weights --------------
        if True == normalize:
            if not self.renormalize_weights():
                return False

        return True

    # renormalize all weights with emphasis on selected vertex group (=bone influence)
    @classmethod
    def renormalize_weights(self, per_vertex: bool = False):
        """Normalize vertex weights while preserving the active group's weighting."""
        with mgtools_functions_log.log_timing("weighting.renormalize_weights"):
            obj = bpy.context.view_layer.objects.active
            if None == obj or 'MESH' != obj.type:
                return False
            if len(obj.vertex_groups) <= 1:
                return True

            mirror_axes = MGTOOLS_functions_helper.get_mirror_axes(obj)
            selection_cached = [vert.select for vert in obj.data.vertices]
            mode_cached = obj.mode
            active_group_cached = obj.vertex_groups.active_index
            tool_settings = bpy.context.scene.tool_settings
            auto_normalize_cached = tool_settings.use_auto_normalize
            selected_indices = [
                index for index, selected in enumerate(selection_cached) if selected
            ]
            weights_before = {}
            success = True

            def snapshot_weights():
                """Capture selected-vertex weights for each vertex group."""
                snapshot = {
                    vertex_group.index: {vertex_index: 0.0 for vertex_index in selected_indices}
                    for vertex_group in obj.vertex_groups
                }
                for vertex_index in selected_indices:
                    for element in obj.data.vertices[vertex_index].groups:
                        if element.group in snapshot:
                            snapshot[element.group][vertex_index] = element.weight
                return snapshot

            try:
                if mirror_axes:
                    weights_before = snapshot_weights()

                if per_vertex:
                    # vertex_weight_normalize_active_vertex requires Weight Paint mode
                    if 'PAINT_WEIGHT' != bpy.context.mode:
                        print("Warning: renormalize_weights(per_vertex=True) requires Weight Paint mode, skipping.")
                        success = False
                        return success
                    bpy.ops.object.vertex_weight_normalize_active_vertex()
                else:
                    # normalize all weights from other bones without changing the weights of the active bone
                    bpy.ops.object.vertex_group_normalize_all(lock_active=True)
                    # normalize all - this will effectively only set vertices of the active bone which don't have any other bone influence to 1
                    bpy.ops.object.vertex_group_normalize_all(lock_active=False)

                if mirror_axes and selected_indices and 'PAINT_WEIGHT' == bpy.context.mode:
                    # Replay only values changed by normalization. Disable automatic
                    # normalization so weight_set() cannot renormalize other groups
                    # while the changed groups are being mirrored one at a time.
                    weights_changed = {}
                    weights_after = snapshot_weights()
                    for vertex_group in obj.vertex_groups:
                        values = weights_after[vertex_group.index]
                        if any(
                            abs(values[vertex_index] - weights_before[vertex_group.index][vertex_index]) > 1e-6
                            for vertex_index in selected_indices
                        ):
                            weights_changed[vertex_group.index] = values

                    tool_settings.use_auto_normalize = False
                    for group_index, values in weights_changed.items():
                        obj.vertex_groups.active_index = group_index
                        self.weight_set_vertices(obj, values)
            except Exception as exc:
                success = False
                mgtools_functions_log.show_exception(
                    exc,
                    message="Weight normalization failed",
                    popup=False,
                    report=False,
                )
            finally:
                tool_settings.use_auto_normalize = auto_normalize_cached
                obj.vertex_groups.active_index = active_group_cached
                for index, selected in enumerate(selection_cached):
                    obj.data.vertices[index].select = selected
                if mode_cached != 'OBJECT' and obj.mode != mode_cached:
                    try:
                        bpy.ops.object.mode_set(mode=mode_cached)
                    except Exception:
                        pass

            return success

    # transfer weights from one vertex group to another of the same mesh
    @classmethod
    def _transfer_weights_for_vertices(self, vg_from, vg_to, vertices, vertex_indices):
        """Add source-group weights to the destination group for given vertices."""
        for idx in vertex_indices:
            # atm we can't simply check if a certain index is defined in the vertex group.
            # So we have to awkwardly ask the mesh vertex if it is part of the group.
            if any(group.group == vg_from.index for group in vertices[idx].groups):
                vg_to.add([idx], vg_from.weight(idx), 'ADD')

    @classmethod
    def transfer_weights(self, vg_from, vg_to, mesh):
        """Transfer weights between groups for every vertex in a mesh."""
        self._transfer_weights_for_vertices(vg_from, vg_to, mesh.vertices, range(len(mesh.vertices)))

    # transfer weights of selected vertices from one vertex group to another of the same mesh
    @classmethod
    def transfer_weights_from_selection(self, vg_from, vg_to, meshobj, vindices, normalize:bool=False):
        """Transfer selected vertex weights and optionally renormalize the result."""
        self._transfer_weights_for_vertices(vg_from, vg_to, meshobj.data.vertices, vindices)
        # normalize weights --------------
        if True == normalize:
            if not self.renormalize_weights():
                return False

        return True

    # Animations #######################################################

    @classmethod
    def motion_path_update(self):
        """Update motion paths when the current Blender context is Pose mode."""
        if 'POSE' != bpy.context.mode:
            return

        print ("update motion paths now!")
        bpy.ops.pose.paths_range_update()
        bpy.ops.pose.paths_update()
        # bpy.ops.pose.paths_calculate()

    
