import bpy
from bpy.types import Operator

from . mgtools_functions_helper import MGTOOLS_functions_helper
from . mgtools_manager_overlays import MGTOOLSOverlayManager


def _active_color_attribute(obj):
    color_attributes = getattr(obj.data, 'color_attributes', None)
    if color_attributes is None:
        return None
    return getattr(color_attributes, 'active_color', None)


def _color_context(operator, context):
    obj = context.view_layer.objects.active
    if obj is None or obj.type != 'MESH':
        operator.report({'ERROR'}, "The active object is not a mesh")
        return None, None
    if context.mode not in {'OBJECT', 'EDIT_MESH', 'PAINT_VERTEX'}:
        operator.report({'ERROR'}, "Use Object, Edit Mesh, or Vertex Paint mode")
        return None, None
    attribute = _active_color_attribute(obj)
    if attribute is None:
        operator.report({'INFO'}, "No active color attribute; this Blender version is not supported")
        return None, None
    if attribute.domain not in {'POINT', 'CORNER'}:
        operator.report({'ERROR'}, "The active color attribute must use Point or Corner domain")
        return None, None
    return obj, attribute


def _selected_indices(obj):
    return [vertex.index for vertex in obj.data.vertices if vertex.select]


def _selected_attribute_values(obj, attribute):
    colors = MGTOOLS_functions_helper.get_color_attribute_colors(obj.data, attribute)
    return [colors[index] for index in _selected_indices(obj)]


def _average_color(values):
    if not values:
        return None
    count = len(values)
    return tuple(sum(value[channel] for value in values) / count for channel in range(4))


def get_selected_color(context):
    obj = context.view_layer.objects.active
    if obj is None or obj.type != 'MESH':
        return None
    attribute = _active_color_attribute(obj)
    if attribute is None:
        return None
    return _average_color(_selected_attribute_values(obj, attribute))


def get_paint_color(context):
    vertex_paint = getattr(context.scene.tool_settings, 'vertex_paint', None)
    brush = getattr(vertex_paint, 'brush', None)
    color = getattr(brush, 'color', None)
    if color is None:
        return None
    return tuple(color[:]) + (1.0,)


def _write_selected_color(obj, attribute, color, channels):
    selected = _selected_indices(obj)
    if not selected:
        return False
    if not channels:
        return False
    data_indices = {
        vertex.index: [vertex.index] if attribute.domain == 'POINT' else [
            loop.index for loop in obj.data.loops if loop.vertex_index == vertex.index
        ]
        for vertex in obj.data.vertices if vertex.index in selected
    }
    for vertex_index in selected:
        for data_index in data_indices[vertex_index]:
            current_color = list(attribute.data[data_index].color[:])
            for channel in channels:
                current_color[channel] = color[channel]
            attribute.data[data_index].color = current_color
    obj.data.update()
    return True


def _offset_selected_color(obj, attribute, channels, amount):
    selected = _selected_indices(obj)
    if not selected:
        return False
    data_indices = {
        vertex.index: [vertex.index] if attribute.domain == 'POINT' else [
            loop.index for loop in obj.data.loops if loop.vertex_index == vertex.index
        ]
        for vertex in obj.data.vertices if vertex.index in selected
    }
    for vertex_index in selected:
        for data_index in data_indices[vertex_index]:
            color = list(attribute.data[data_index].color[:])
            for channel in channels:
                color[channel] = max(0.0, min(1.0, color[channel] + amount))
            attribute.data[data_index].color = color
    obj.data.update()
    return True


class MGTOOLS_vertex_color_operator:
    @classmethod
    def poll(cls, context):
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == 'MESH'


class MGTOOLS_OT_vertex_color_sample(MGTOOLS_vertex_color_operator, Operator):
    bl_idname = "mgtools.vertex_color_sample"
    bl_label = "Sample Vertex Color"
    bl_description = "Sample the average color of the selected vertices"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj, attribute = _color_context(self, context)
        if obj is None:
            return {'CANCELLED'}
        color = _average_color(_selected_attribute_values(obj, attribute))
        if color is None:
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}
        context.scene.mgtools.p_vertexcolor_selected = color
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_set( MGTOOLS_vertex_color_operator, Operator):
    bl_idname = "mgtools.vertex_color_set"
    bl_label = "Set Vertex Color"
    bl_description = "Set the active color on selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    color: bpy.props.FloatVectorProperty(
        name="Color", subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )
    channels: bpy.props.BoolVectorProperty(
        name="Channels", size=4, default=(True, False, False, False),
    )

    def execute(self, context):
        obj, attribute = _color_context(self, context)
        if obj is None:
            return {'CANCELLED'}
        active_channels = [index for index, enabled in enumerate(self.channels) if enabled]
        if not active_channels:
            self.report({'WARNING'}, "Select at least one channel")
            return {'CANCELLED'}
        if not _write_selected_color(obj, attribute, self.color, active_channels):
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_offset( MGTOOLS_vertex_color_operator, Operator):
    bl_idname = "mgtools.vertex_color_offset"
    bl_label = "Offset Vertex Color"
    bl_description = "Add or subtract a value from one color channel on selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    channels: bpy.props.BoolVectorProperty(
        name="Channels", size=4, default=(True, False, False, False),
    )
    amount: bpy.props.FloatProperty(name="Amount", default=0.1, min=0.0, max=1.0, precision=3)

    def execute(self, context):
        obj, attribute = _color_context(self, context)
        if obj is None:
            return {'CANCELLED'}
        amount = self.amount if self.amount >= 0.0 else -self.amount
        active_channels = [index for index, enabled in enumerate(self.channels) if enabled]
        if not active_channels:
            self.report({'WARNING'}, "Select at least one channel")
            return {'CANCELLED'}
        if not _offset_selected_color(obj, attribute, active_channels, amount):
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_subtract( MGTOOLS_vertex_color_operator, Operator):
    bl_idname = "mgtools.vertex_color_subtract"
    bl_label = "Subtract Vertex Color"
    bl_description = "Subtract a value from one color channel on selected vertices"

    channels: bpy.props.BoolVectorProperty(
        name="Channels", size=4, default=(True, False, False, False),
    )
    amount: bpy.props.FloatProperty(name="Amount", default=0.1, min=0.0, max=1.0, precision=3)

    def execute(self, context):
        obj, attribute = _color_context(self, context)
        if obj is None:
            return {'CANCELLED'}
        active_channels = [index for index, enabled in enumerate(self.channels) if enabled]
        if not active_channels:
            self.report({'WARNING'}, "Select at least one channel")
            return {'CANCELLED'}
        if not _offset_selected_color(obj, attribute, active_channels, -self.amount):
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_show(Operator):
    bl_idname = "mgtools.vertex_color_show"
    bl_label = "Show Vertex Colors"
    bl_description = "Draw active vertex colors as dots over vertices"
    bl_options = {'REGISTER'}

    def execute(self, context):
        MGTOOLSOverlayManager.init()
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_hide(Operator):
    bl_idname = "mgtools.vertex_color_hide"
    bl_label = "Hide Vertex Colors"
    bl_description = "Stop drawing vertex colors as dots over vertices"
    bl_options = {'REGISTER'}

    def execute(self, context):
        MGTOOLSOverlayManager.deinit()
        return {'FINISHED'}


class MGTOOLS_OT_vertex_color_smooth(Operator):
    bl_idname = "mgtools.vertex_color_smooth"
    bl_label = "Smooth Vertex Colors"
    bl_description = "Smooth the active vertex color attribute"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'PAINT_VERTEX'

    def execute(self, context):
        try:
            result = bpy.ops.paint.vertex_color_smooth()
        except RuntimeError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return result
