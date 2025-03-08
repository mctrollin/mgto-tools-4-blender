import bpy
import mathutils
from mathutils import Vector, Euler, Matrix
import uuid
from . mgtools_functions_helper import MGTOOLS_functions_helper

class MGTOOLS_functions_macros():


    # Object.Selection #######################################################

    @classmethod
    def get_first_selected_mesh(self):
        for tmpObj in bpy.context.selected_objects:
            if 'MESH' == tmpObj.type:
                return tmpObj

    @classmethod
    def get_first_selected_armature(self):
        for tmpObj in bpy.context.selected_objects:
            if 'ARMATURE' == tmpObj.type:
                return tmpObj
            else:
                print ("{} is {}".format(tmpObj, tmpObj.type))

    @classmethod
    def get_armature_from_first_selected_mesh(self):
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
        if None == refobj:
            return
        if type(refobj) == list:
            print("Warning: input should be one object but its:{}".format(len(refobj)))
            return

        # clear selection
        for obj in bpy.data.objects:
            obj.select_set(False)

        # select only our mesh object
        refobj.select_set(True)
        bpy.context.view_layer.objects.active = refobj

    @classmethod
    def select_objects(self, ref_objects, set_active:bool=False):

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


    # Object.Misc #######################################################

    # Duplicate selected objects and move them into a newly created collection
    @classmethod
    def duplicate_to_collection(self, source_objects, select_clones):
        
        # cache current selection
        cached_selection = bpy.context.selected_objects
        cached_active = bpy.context.view_layer.objects.active

        # set selection
        self.select_objects(source_objects, True)
        
        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting object for duplication: {}".format(source_object))
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
            self.select_objects(cached_selection, False)
            bpy.context.view_layer.objects.active = cached_active
        else:
            self.select_objects(clones_meshes, True)

        return tmp_export_collection

    # De-instanciate a collection instance and remove the parent null objects
    @classmethod
    def make_collection_instance_real(self, collection_instance):

        if None == collection_instance:
            return

        if None == collection_instance.instance_collection:
            return

        # cache current selection
        cached_selection = bpy.context.selected_objects
        cached_active = bpy.context.view_layer.objects.active

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
        self.select_objects(cached_selection, False)
        bpy.context.view_layer.objects.active = cached_active
        # else:
        #     self.select_objects(clones_meshes, True)

        return childs_all


    # Object.Manipulation #######################################################

    @classmethod
    def make_snapshot_from(self, source_objects_raw, merge, prefix, postfix, select_clones, type_filter):
        
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
        cached_selection = bpy.context.selected_objects
        cached_active = bpy.context.view_layer.objects.active
        
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
            if 'MESH' == source_object.type:
                if True == merge:
                    # apply all modifiers
                    MGTOOLS_functions_helper.apply_modifiers_smartly(clone)
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
            self.select_objects(cached_selection, False)
            bpy.context.view_layer.objects.active = cached_active
        else:
            self.select_objects(clones_meshes, True)

        return clones

    @classmethod
    def set_pivot(self, target_objects, new_loc=(0,0,0), new_rot_euler=(0,0,0), new_scale=(1,1,1), apply_scale=False):
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
        active_object_cached = bpy.context.view_layer.objects.active
        selected_objects_cached = bpy.context.selected_objects

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
        bpy.context.view_layer.objects.active = active_object_cached
        self.select_objects(selected_objects_cached, False)

    @classmethod
    def zero_pivot_to(self, target_objects, location):
        # Prepare -------------------------------------------
        # Cache cursor transforms
        location_cached = bpy.context.scene.cursor.location

        # Cache selection
        active_object_cached = bpy.context.view_layer.objects.active
        selected_objects_cached = bpy.context.selected_objects

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
        bpy.context.view_layer.objects.active = active_object_cached
        self.select_objects(selected_objects_cached, False)  


    # Modifier #######################################################


    # Armature #######################################################


    # Weighting #######################################################

    # mode can be 'REPLACE', 'ADD' or 'SUBTRACT'
    @classmethod
    def set_weights_to_selected_mesh(self, weight:float, mode:str, normalize:bool=False):
        # get mesh object
        meshobj = self.get_first_selected_mesh()
        if None == meshobj:
            print("Not a mesh")
            return

        # get vertex group
        activeVG = meshobj.vertex_groups.active
        if None == activeVG:
            print("No active vertex group")
            return

        # get selected vertices
        selected_vert_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)

        # set weight
        MGTOOLS_functions_helper.set_weights(activeVG, selected_vert_indices, weight, mode)

        # normalize weights --------------
        if True == normalize:
            self.renormalize_weights()

    # renormalize all weights with emphasis on selected vertex group (=bone influence)
    @classmethod
    def renormalize_weights(self):
        # normalize all weights from other bones without changing the weights of the active bone
        bpy.ops.object.vertex_group_normalize_all(lock_active=True)
        # normalize all - this will effectively only set vertices of the active bone which don't have any other bone influence to 1
        bpy.ops.object.vertex_group_normalize_all(lock_active=False)

    # transfer weights from one vertex group to another of the same mesh
    @classmethod
    def transfer_weights(self, vg_from, vg_to, mesh):
        for idx in range(len(mesh.vertices)):
            # atm we can't simply check if a certain index is defined in the vertex group. 
            # So we have to awkwardly ask the mesh vertex if it is part of the group. 
            # I hope this will be improved in the future
            if [True for g in mesh.vertices[idx].groups if g.group == vg_from.index]:
                vg_to.add([idx], vg_from.weight(idx), 'ADD')

    # transfer weights of selected vertices from one vertex group to another of the same mesh
    @classmethod
    def transfer_weights_from_selection(self, vg_from, vg_to, meshobj, vindices, normalize:bool=False):
        for idx in vindices:
            # atm we can't simply check if a certain index is defined in the vertex group. 
            # So we have to awkwardly ask the mesh vertex if it is part of the group. 
            # I hope this will be improved in the future
            if [True for g in meshobj.data.vertices[idx].groups if g.group == vg_from.index]:
                vg_to.add([idx], vg_from.weight(idx), 'ADD')
        # normalize weights --------------
        if True == normalize:
            self.renormalize_weights()

    # Animations #######################################################

    @classmethod
    def motion_path_update(self):
        if 'POSE' != bpy.context.mode:
            return

        print ("update motion paths now!")
        bpy.ops.pose.paths_range_update()
        bpy.ops.pose.paths_update()
        # bpy.ops.pose.paths_calculate()

    
