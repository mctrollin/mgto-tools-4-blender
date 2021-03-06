import bpy
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
    def select_objects(self, ref_objects, set_active):

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

        if None == collection_instance.instance_collection:
            return

        # cache current selection
        cached_selection = bpy.context.selected_objects
        cached_active = bpy.context.view_layer.objects.active

        # --------------------------------------------

        # set selection
        MGTOOLS_functions_macros.select_only(collection_instance)

        # keep parent and hierarchy, we only want to get rid of the instance-state for now
        bpy.ops.object.duplicates_make_real(
            use_base_parent=True, use_hierarchy=True)

        # get children
        childs = []
        childs.extend(collection_instance.children)

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

        return childs


    # Object.Manipulation #######################################################

    @classmethod
    def make_snapshot_from(self, source_objects_raw, merge, prefix, posfix, select_clones, type_filter):
        if None == source_objects_raw or 0 >= len(source_objects_raw):
            return

        # prepare source objects list
        source_objects = []
        if None != type_filter and 0 < len(type_filter):
            for source_object in source_objects_raw:
                if type_filter == source_object.type:
                    source_objects.append(source_object)
            if 0 >= len(source_objects):
                return
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
        
        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting object for duplication: {}".format(source_object))
            return

        # create a copy of all selected objects and select these
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')

        if 0 >= len(bpy.context.selected_objects):
            print("Problem selecting clone of: {}".format(source_object))
            return
        
        clones = bpy.context.selected_objects.copy()

        print(" > processing duplicates: {}".format(clones))
        for idx, clone in enumerate(clones):
            
            self.select_only(clone)
            source_object = source_objects[idx]

            # add name pre- and posfix
            new_name = source_object.name

            if 0 < len(prefix): 
                new_name = prefix + new_name

            if 0 < len(posfix):
                new_name = new_name + posfix

            clone.name = new_name

            # mesh specific processing
            if 'MESH' == source_object.type:
                # apply all modifiers
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

        # select clones for further processing with bpy.ops
        self.select_objects(clones_meshes, True)

        # option: join clones_meshes
        if True == merge:
            if 1 < len(clones_meshes):
                print(" > joining objects: {}".format(clones_meshes))
                ctx = bpy.context.copy()
                ctx['selected_objects'] = clones_meshes
                bpy.ops.object.join(ctx)
                clones_meshes = bpy.context.selected_objects
                for clone_meshes in clones_meshes:
                    clone_meshes.name += "_merged"

        # get list of all final clones
        clones = clones_other + clones_meshes

        # option: revert selection or not
        # print(" > set selection")
        if False == select_clones:
            self.select_objects(cached_selection, False)
            bpy.context.view_layer.objects.active = cached_active
        else:
            self.select_objects(clones_meshes, True)

        return clones

    @classmethod
    def set_pivot(self, target_objects, new_loc, new_rot_euler, apply_scale):
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
            MGTOOLS_functions_helper.set_parent(target_object, None, True)

        # Position -------------------------------------------
        # Set origin location to cursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Rotation -------------------------------------------
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=apply_scale)
        
        new_rot_mat = new_rot_euler.to_matrix()
        new_rot_mat_twice = new_rot_mat @ new_rot_mat
        new_rot_euler_twice_inverted = new_rot_mat_twice.inverted().to_euler()

        for obj in target_objects:
            # 'apply' or 'freeze' rotation
            obj.delta_rotation_euler = new_rot_euler 
             # revert back so object stays in place and pivot matches target
            obj.rotation_euler = new_rot_euler_twice_inverted
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        # Reset parents -------------------------------------------
        for i, target_object in enumerate(target_objects):
            # re-parent
            MGTOOLS_functions_helper.set_parent(target_object, parents_cache[i], True)

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
    def set_weights_to_selected_mesh(self, weight, mode):
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
        self.renormalize_weights()

    # renormalize all weights with emphasis on selected vertex group (=bone influence)
    @classmethod
    def renormalize_weights(self):
        # normalize all weights from other bones without changing the weights of the active bone
        bpy.ops.object.vertex_group_normalize_all(lock_active=True)
        # normalize all - this will effectively only set vertices of the active bone which don't have any other bone influence to 1
        bpy.ops.object.vertex_group_normalize_all(lock_active=False)


    # Animations #######################################################

    @classmethod
    def motion_path_update(self):
        if 'POSE' != bpy.context.mode:
            return

        print ("update motion paths now!")
        bpy.ops.pose.paths_range_update()
        bpy.ops.pose.paths_update()
        # bpy.ops.pose.paths_calculate()

    
