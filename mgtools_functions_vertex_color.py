import bpy


class MGTOOLS_functions_vertex_color():

    @classmethod
    def get_bake_to_vcolors_errors(self, obj, attribute_name=None, channel=None, samples=100,
                                   check_cycles=True):
        errors = []
        if obj is None or obj.type != 'MESH':
            errors.append('Bake target must be a mesh object')
            return errors

        color_attributes = getattr(obj.data, 'color_attributes', None)
        if color_attributes is None:
            errors.append('This Blender version does not support color attributes')
            return errors

        attribute = color_attributes.get(attribute_name) if attribute_name else color_attributes.active_color
        if attribute is None:
            errors.append('Bake target color attribute was not found')
        else:
            if attribute.domain not in {'POINT', 'CORNER'}:
                errors.append('Bake target color attribute must use Point or Corner domain')
            if attribute.data_type not in {'BYTE_COLOR', 'FLOAT_COLOR'}:
                errors.append('Bake target color attribute must store color data')

        if channel is not None and channel not in range(4):
            errors.append('Bake channel must be between 0 and 3')
        if samples < 1:
            errors.append('Bake samples must be at least 1')
        if check_cycles and getattr(bpy.context.scene, 'cycles', None) is None:
            errors.append('Cycles rendering engine is unavailable')
        return errors

    @classmethod
    def write_vcolors_attribute_channel(self, obj, attribute_name, channel, value):
        color_attributes = getattr(obj.data, 'color_attributes', None)
        if color_attributes is None:
            raise RuntimeError('This Blender version does not support color attributes')
        attribute = color_attributes.get(attribute_name) if attribute_name else color_attributes.active_color
        if attribute is None:
            raise RuntimeError('Bake target color attribute was not found')
        if channel not in range(4):
            raise RuntimeError('Bake channel must be between 0 and 3')
        for item in attribute.data:
            color = list(item.color[:])
            color[channel] = value
            item.color = color
        obj.data.update()

    @classmethod
    def bake_to_vcolors_attribute(self, obj, bake_type, attribute_name=None, channel=None, samples=100):
        """Bake a Cycles pass to a mesh vertex-color attribute."""
        errors = self.get_bake_to_vcolors_errors(obj, attribute_name, channel, samples)
        if errors:
            raise RuntimeError(errors[0])

        color_attributes = obj.data.color_attributes
        destination = color_attributes.get(attribute_name) if attribute_name else color_attributes.active_color

        active_index = color_attributes.active_color_index
        original_engine = bpy.context.scene.render.engine
        cycles_settings = getattr(bpy.context.scene, 'cycles', None)
        original_samples = getattr(cycles_settings, 'samples', None)
        original_bake_type = getattr(cycles_settings, 'bake_type', None)
        active_object = bpy.context.view_layer.objects.active
        selected_objects = list(bpy.context.selected_objects)
        original_mode = active_object.mode if active_object is not None else 'OBJECT'
        temporary = None
        try:
            bake_attribute = destination
            if channel is not None:
                # Bake the selected channel into a temporary layer so the other channels survive.
                temporary_name = '__mgtools_bake_result'
                suffix = 1
                while color_attributes.get(temporary_name) is not None:
                    temporary_name = '__mgtools_bake_result_{}'.format(suffix)
                    suffix += 1
                temporary = color_attributes.new(
                    name=temporary_name, type=destination.data_type, domain=destination.domain)
                bake_attribute = temporary

            color_attributes.active_color_index = color_attributes.find(bake_attribute.name)
            if bpy.context.object and bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.context.scene.render.engine = 'CYCLES'
            if cycles_settings is not None and hasattr(cycles_settings, 'bake_type'):
                cycles_settings.bake_type = bake_type
            if cycles_settings is not None and hasattr(cycles_settings, 'samples'):
                cycles_settings.samples = samples

            # Blender must evaluate the new active layer and clone geometry before baking.
            obj.data.update()
            bpy.context.view_layer.update()

            result = bpy.ops.object.bake(type=bake_type, target='VERTEX_COLORS', use_clear=False)
            if 'FINISHED' not in result:
                raise RuntimeError('Blender did not finish the color bake')

            if channel is not None:
                # Copy only the requested result channel back to the destination layer.
                for destination_item, baked_item in zip(destination.data, temporary.data):
                    color = list(destination_item.color[:])
                    color[channel] = baked_item.color[channel]
                    destination_item.color = color
                obj.data.update()
        finally:
            # Restore Blender state even when Cycles or a later channel raises.
            if temporary is not None and color_attributes.get(temporary.name) is not None:
                color_attributes.remove(temporary)
            if len(color_attributes):
                color_attributes.active_color_index = min(active_index, len(color_attributes) - 1)
            bpy.context.scene.render.engine = original_engine
            if original_bake_type is not None:
                bpy.context.scene.cycles.bake_type = original_bake_type
            if original_samples is not None:
                bpy.context.scene.cycles.samples = original_samples
            bpy.ops.object.select_all(action='DESELECT')
            for selected_object in selected_objects:
                if selected_object.name in bpy.data.objects:
                    selected_object.select_set(True)
            bpy.context.view_layer.objects.active = active_object
            if active_object is not None and original_mode != 'OBJECT' and active_object.mode != original_mode:
                bpy.ops.object.mode_set(mode=original_mode)
        return True
