import bpy
from bpy.types import Operator
from . mgtools_manager_overlays import MGTOOLSOverlayManager
from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_functions_macros import MGTOOLS_functions_macros

# show colored vertices
class MGTOOLS_OT_weighting_show_weights(Operator):
    bl_idname =  "mgtools.weighting_show_weights"
    bl_label = "Show vertex weights"
    bl_description = "Draw vertex weights as dots over vertices"
    bl_options = {'REGISTER'}    

    def execute(self, context):
        MGTOOLSOverlayManager.init()
        return {'FINISHED'}
# hide colored vertices
class MGTOOLS_OT_weighting_hide_weights(Operator):
    bl_idname =  "mgtools.weighting_hide_weights"
    bl_label = "Hide vertex weights"
    bl_description = "Stops drawing vertex weights as dots over vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLSOverlayManager.deinit()
        return {'FINISHED'}

# set weight
class MGTOOLS_OT_weighting_set_weights(Operator):
    bl_idname =  "mgtools.weighting_set_weights"
    bl_label = "Set vertex weights"
    bl_description = "Set a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        # bpy.context.scene.tool_settings.unified_paint_settings.weight = 0.5
        bpy.ops.paint.weight_set()
        MGTOOLS_functions_macros.renormalize_weights()
        return {'FINISHED'}
# add weight
class MGTOOLS_OT_weighting_add_weights(Operator):
    bl_idname =  "mgtools.weighting_add_weights"
    bl_label = "Add vertex weights"
    bl_description = "Add a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        mgtools_props_obj = bpy.context.object.mgtools
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(mgtools_props_obj.p_weightedit_add_amount, 'ADD', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# substract weight
class MGTOOLS_OT_weighting_subtract_weights(Operator):
    bl_idname =  "mgtools.weighting_subtract_weights"
    bl_label = "Substract vertex weights"
    bl_description = "Substract a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        mgtools_props_obj = bpy.context.object.mgtools
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(mgtools_props_obj.p_weightedit_add_amount, 'SUBTRACT', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}

# set weight to 0.0
class MGTOOLS_OT_weighting_set_weights_to_0(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_0"
    bl_label = "Set vertex weights to 0"
    bl_description = "Set weigh of selected vertices to 0"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 0.1
class MGTOOLS_OT_weighting_set_weights_to_01(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_01"
    bl_label = "Set vertex weights to 0.1"
    bl_description = "Set weigh of selected vertices to 0.1"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.1, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 0.25
class MGTOOLS_OT_weighting_set_weights_to_025(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_025"
    bl_label = "Set vertex weights to 0.25"
    bl_description = "Set weigh of selected vertices to 0.25"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.25, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 0.5
class MGTOOLS_OT_weighting_set_weights_to_05(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_05"
    bl_label = "Set vertex weights to 0.5"
    bl_description = "Set weigh of selected vertices to 0.5"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.5, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 0.75
class MGTOOLS_OT_weighting_set_weights_to_075(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_075"
    bl_label = "Set vertex weights to 0.75"
    bl_description = "Set weigh of selected vertices to 0.75"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.75, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 0.9
class MGTOOLS_OT_weighting_set_weights_to_09(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_09"
    bl_label = "Set vertex weights to 0.9"
    bl_description = "Set weigh of selected vertices to 0.9"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(0.9, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}
# set weight to 1.0
class MGTOOLS_OT_weighting_set_weights_to_1(Operator):
    bl_idname =  "mgtools.weighting_set_weights_to_1"
    bl_label = "Set vertex weights to 1"
    bl_description = "Set weigh of selected vertices to 1"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        MGTOOLS_functions_macros.set_weights_to_selected_mesh(1, 'REPLACE', bpy.context.scene.tool_settings.use_auto_normalize)
        return {'FINISHED'}

# mirror all weights from all vertices along the y-z-plane from -x to +x
class MGTOOLS_OT_weighting_quick_mirror(Operator):
    bl_idname =  "mgtools.weighting_quick_mirror"
    bl_label = "Quick Mirror X"
    bl_description = "Mirror all weights from all vertices along the y-z-plane from -x to +x"
    bl_options = {'REGISTER'} 

    def execute(self, context):	

        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        selection_cached = [False for i in range(len(meshobj.data.vertices))]

        # loop over all vertices and select all on the side we want to mirror to
        for vert in meshobj.data.vertices:
            local_vert_pos = meshobj.matrix_parent_inverse @ vert.co
            # select all vertices on one side of the y-z-plane
            selection_cached[vert.index] = vert.select
            vert.select = 0 < local_vert_pos.x

        # properties
        mgtools_props_obj = bpy.context.object.mgtools

        # class mirror operator
        bpy.ops.object.vertex_group_mirror(
            mirror_weights=True, 
            flip_group_names=True, 
            all_groups=mgtools_props_obj.p_weightedit_mirror_all_groups, 
            use_topology=mgtools_props_obj.p_weightedit_mirror_use_topology)
        
        # revert selection
        for vert in meshobj.data.vertices:
            vert.select = selection_cached[vert.index]

        return {'FINISHED'}



# set weights of selected vertices to their mean
class MGTOOLS_OT_weighting_average_weights(Operator):
    bl_idname =  "mgtools.weighting_average_weights"
    bl_label = "Substract vertex weights"
    bl_description = "Substract a defined amount of weigh to the selected vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):	
        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        vgroups = meshobj.vertex_groups

        if 0 >= len(vgroups):
            print("Model has no vertex groups")
            return {'CANCELLED'}
        
        # get selected verts
        selected_verts_indices = MGTOOLS_functions_helper.get_selected_vert_indicies(meshobj)

        if 0 >= len(selected_verts_indices):
            print("No vertices selected")
            return {'CANCELLED'}

        # calculate average weights and assign them
        for idx, vg in enumerate(vgroups):
            weight_average = MGTOOLS_functions_helper.get_weight_average(meshobj, idx, selected_verts_indices)
            MGTOOLS_functions_helper.set_weights(vg, selected_verts_indices, weight_average, 'REPLACE')

        return {'FINISHED'}

class MGTOOLS_OT_weighting_create_vertex_groups_for_selected_bones(Operator):
    bl_idname =  "mgtools.weighting_create_vertex_groups_for_selected_bones"
    bl_label = "Create vertex groups"
    bl_description = "Create missing vertex groups on active mesh for selected pose bones. Note: make sure to use an armature modifier!"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        # prepare vars
        obj = context.view_layer.objects.active
        selected_bones = context.selected_pose_bones # context.selected_bones
        
        if None == selected_bones or 0 >= len(selected_bones): 
            print("No pose bones selected")
            return {'CANCELLED'}

        bone_names = [bone.name for bone in selected_bones]
        print("obj: {}, bone_names: {}".format(obj, bone_names))
        # create vertex groups
        MGTOOLS_functions_helper.create_vgroups_from_names(obj, bone_names)
        return {'FINISHED'}

class MGTOOLS_OT_weighting_remove_vertex_groups_unused(Operator):
    bl_idname =  "mgtools.weighting_remove_vertex_groups_unused"
    bl_label = "Remove unused vertex groups"
    bl_description = "Remove all vertex groups without any assigned vertices"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        meshobj = MGTOOLS_functions_macros.get_first_selected_mesh()
        if None == meshobj:
            print("No mesh object selected")
            return {'CANCELLED'}

        vgroups = meshobj.vertex_groups

        if 0 >= len(vgroups):
            print("Model has no vertex groups")
            return {'CANCELLED'}

        # properties
        mgtools_props_obj = bpy.context.object.mgtools
        
        # prepare vars
        only_unused = mgtools_props_obj.p_weightedit_remove_empty
        include_locked = mgtools_props_obj.p_weightedit_remove_locked

        MGTOOLS_functions_helper.remove_vgroups(meshobj, only_unused, include_locked)


        return {'FINISHED'}


class MGTOOLS_OT_weighting_set_max_influences(Operator):
    bl_idname =  "mgtools.weighting_set_max_influences"
    bl_label = "Set max influences"
    bl_description = "Keep only the strongest influences up to the maximum allowed amount of total influences per bone"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        # properties
        mgtools_props_obj = bpy.context.object.mgtools
        
        # prepare vars
        max_influences = mgtools_props_obj.p_weightedit_max_influences
        obj = context.view_layer.objects.active
        if None == obj or 'MESH' != obj.type:
            return {'FINISHED'}
        armature_modifier = MGTOOLS_functions_helper.get_all_modifier(obj, 'ARMATURE')
        armatures = []
        for amod in armature_modifier:
            armatures.append(amod.object)

        # process
        for armature in armatures:
            MGTOOLS_functions_helper.remove_lowest_weights(obj, armature, max_influences)

        return {'FINISHED'}

class MGTOOLS_OT_weighting_set_min_influence(Operator):
    bl_idname =  "mgtools.weighting_set_min_influence"
    bl_label = "Set min influence"
    bl_description = "Remove all influences which are below the minimum required influence per bone"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        # properties
        mgtools_props_obj = bpy.context.object.mgtools

        # prepare vars
        weight_threshold = mgtools_props_obj.p_weightedit_min_weight
        obj = context.view_layer.objects.active
        if None == obj or 'MESH' != obj.type:
            return {'FINISHED'}
        armature_modifier = MGTOOLS_functions_helper.get_all_modifier(obj, 'ARMATURE')
        armatures = []
        for amod in armature_modifier:
            armatures.append(amod.object)

        # process
        for armature in armatures:
            MGTOOLS_functions_helper.remove_weights_below_threshold(obj, armature, weight_threshold)
        return {'FINISHED'}