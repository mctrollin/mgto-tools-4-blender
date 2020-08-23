import bpy
import colorsys
from mathutils import Matrix # Vector, Euler, 

class MGTOOLS_functions_helper():

    # Selection.Mesh #######################################################
    
    @classmethod
    def get_selected_verts(self, meshobj):
        return [v for v in meshobj.data.vertices if v.select]

    @classmethod
    def get_selected_vert_indicies(self, meshobj):
        selected_verts = self.get_selected_verts(meshobj)
        selected_vert_indices = [v.index for v in selected_verts]
        return selected_vert_indices


    # Objects #######################################################

    @classmethod
    def set_parent(self, child, new_parent, keep_transforms):
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


    # Modifier #######################################################

    @classmethod
    def get_all_modifier(self, source_object, modifier_type):
        modifier = []
        # print("  checking {}".format(source_object))
        for mod in source_object.modifiers:
            # print("    checking {}, {}".format(mod, mod.type))
            # armatures
            if modifier_type == mod.type:
                modifier.append(mod)
        return modifier

    @classmethod
    def transfere_modifier_armature(self, source_objects, target_objects):
        print ("transfere_modifier_armature()")
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
                    if False == (armature in armatures):
                        armatures.append(armature)

        # noting to copy
        if 1 > len(armatures):
            print (" > No armatures found")
            return

        # too much to copy
        if 1 < len(armatures):
            print (" > More then one target Armature detected. This is currently not supported: {}".format(armatures))
            return

        # target objects shouldn't have an armature modifier applied 
        for target_object in target_objects:
            target_object.modifiers.new(name="Armature", type='ARMATURE')
            target_object.modifiers["Armature"].object = armatures[0]


    # View Layer / Collection #######################################################

    # check all of the top level LayerCollections and recursively all of their child LayerCollections
    @classmethod
    def get_layercollection(self, collection):
        lc_out = None
        for lc in bpy.context.view_layer.layer_collection.children:
            lc_out = self.get_layercollection_r(lc, collection)
            if None != lc_out:
                return lc_out

    # try find the related LayerCollection to a supplied Collection (recursive)
    @classmethod
    def get_layercollection_r(self, layer_collection, collection):
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


    # Vertex Groups #######################################################

    @classmethod
    def try_get_vgroup(self, vgroup_name):
        return ob.data.vertices.groups[vgroup_name]

    # returns all vertex groups which belong to an armature bone
    @classmethod
    def get_bone_vgroups(self, obj, armature):
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
            vg = meshobj.vertex_groups[vge.group]
            # check if there exists a bone with the same name in the supplied armature
            if True == any(bone.name == vg.name for bone in armature.data.bones): # vg.name in armature.bones:
                vgroups_bones.append(vge)
        return vgroups_bones

    @classmethod
    def get_bone_vgroups_from_vert(self, meshobj, vert_idx, armature):
        vgelements = self.get_bone_vgelements_from_vert(meshobj, vert_idx, armature)
        vgroups = []
        for vge in vgelements:
            vgroups.append(meshobj.vertex_groups[vge.group])
        return vgroups

    @classmethod
    def create_vgroups_from_names(self, meshobj, vg_names):
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


    # Armature #######################################################


    # Weighting #######################################################

    # mode can be 'REPLACE', 'ADD' or 'SUBTRACT'
    @classmethod
    def set_weights(self, vgroup, vindices, weight, mode):
        vgroup.add(vindices, weight, mode)

    # returns (for a given mesh and a given vertex group) a list with the weight of every vertice
    # Note: it will return a weight of 0 even if the vertex is not part of the vertex group
    @classmethod
    def get_weights(self, mesh, vgroup):
        weights = []
        group_index = vgroup.index
        # for i, v in enumerate(mesh.vertices):
        for v in mesh.vertices:
            weight = 0
            for vge in v.groups:
                if vge.group != group_index:
                    continue           
                weight = vge.weight
                break
            weights.append(weight)
        return weights

    # returns the average weight of all supplied vertices within the given vertex group
    @classmethod
    def get_weight_average(self, meshobj, vgroupidx, vindices):
        weight_average = 0
        selected_vert_indices = vindices
        selected_verts_count = len(selected_vert_indices)
        # if nothing is selected just exit
        if 0 >= selected_verts_count:
            return weight_average

        # get weights
        # weights = list(range(0,1000))
        weights = MGTOOLS_functions_helper.get_weights(meshobj.data, meshobj.vertex_groups[vgroupidx])
        
        # accumulate weights
        weight_accum = 0
        for idx in selected_vert_indices:
            weight_accum += weights[idx]

        # calculate average
        weight_average = weight_accum / selected_verts_count
        return weight_average

    # for every vertex remove all weights except the highest ones up the supplied maximum count
    @classmethod
    def remove_lowest_weights(self, meshobj, armature, max_influences):
        print("remove_lowest_weights()")

        # check if meshobj is really a mesh type
        if 'MESH' != meshobj.type:
            return
        if 'ARMATURE' != armature.type:
            return

        # for every vertex
        for i, vert in enumerate(meshobj.data.vertices):
            # get only vertex groups elements which belong to a bone
            vert_vges = self.get_bone_vgelements_from_vert(meshobj, i, armature)

            # continue if this vertex doesn't use more influences then allowed
            if max_influences >= len(vert_vges):
                continue

            # print ("  > checking vert: {} influences: {}".format(i, len(vert_vges)))

            # sort vertex groups by influence value
            vert_vges.sort(key=lambda x: x.weight, reverse=True)

            # resize to maximum allowed amount of influences
            vgroups_keep = vert_vges[:max_influences]

            # remove weights
            for vge in vert_vges:
                if vge in vgroups_keep:
                    continue
                # get vertex group
                vg = meshobj.vertex_groups[vge.group]
                # remove vertex from group
                vg.remove([i])
                print ("    removing vert {} with weight: {} from vg: {}".format(i, vge.weight, vg.name))

    # for every vertex set all weights to zero which are below the threshold
    @classmethod
    def remove_weights_below_threshold(self, meshobj, armature, threshold):
        print("remove_weights_below_threshold()")
        
        # check if meshobj is really a mesh type
        if 'MESH' != meshobj.type:
            return
        if 'ARMATURE' != armature.type:
            return

        #for every vertex
        for i, vert in enumerate(meshobj.data.vertices):
            # print ("  > checking vert: {}".format(i))
            # get only vertex groups elements which belong to a bone
            vert_vges = self.get_bone_vgelements_from_vert(meshobj, i, armature)
            # for every bone...
            for vge in vert_vges:
                # if below threshould set weight to 0
                if threshold <= vge.weight:
                    continue
                # get vertex group
                vg = meshobj.vertex_groups[vge.group]
                # remove vertex from group
                vg.remove([i])
                print ("    removing vert {} with weight: {} from vg: {}".format(i, vge.weight, vg.name))


    # Animations #######################################################

    # Retrieve all actions given a blender object. Includes NLA-actions
    @classmethod
    def get_all_actions(self, obj):
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
                target_strip = target_nla_track.strips.new(source_strip.action.name, source_strip.frame_start, source_strip.action)
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
    def convertWeight2Color(self, value):
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
        # transform intrinsic- to world-space
        if None == obj:
            return (0, 0, 0)
        if None == obj.parent:
            return obj.location
        ao_pos_i = obj.location
        ao_pos_l = obj.matrix_parent_inverse @ ao_pos_i
        ao_pos_w = obj.parent.matrix_world @ ao_pos_l
        return ao_pos_w