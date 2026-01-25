"""Compatibility helpers for different Blender API versions.

Purpose: centralize version detection and small shims so the rest of the addon
can call compat.get_unified_paint_settings(...), compat.template_list(...)
etc. without sprinkling version checks across the codebase.

Keep this module minimal and explicit: add a new shim for each API change.
"""
from __future__ import annotations

import bpy
from typing import Any, Iterable, Tuple, Optional

# Public version tuple (major, minor, patch)
VERSION: Tuple[int, int, int] = bpy.app.version
IS_5_0: bool = VERSION >= (5, 0, 0)


def _detect_path_supports_blend_relative() -> bool:
    """Detect whether `StringProperty` supports options={'PATH_SUPPORTS_BLEND_RELATIVE'}.

    Use a version-based check instead of probing the API at runtime. The
    PATH_SUPPORTS_BLEND_RELATIVE option was introduced in Blender 4.5, so we
    consider any Blender >= 4.5 to have support.
    """
    return VERSION >= (4, 5, 0)


# Whether the bpy.props StringProperty accepts the PATH_SUPPORTS_BLEND_RELATIVE option
SUPPORTS_PATH_SUPPORTS_BLEND_RELATIVE: bool = _detect_path_supports_blend_relative()


def StringProperty(*args, **kwargs):
    """Compatibility wrapper around `bpy.props.StringProperty`.

    - Removes the option key `'PATH_SUPPORTS_BLEND_RELATIVE'` when the running
      Blender version doesn't support it.
    - On TypeError (very old Blender versions that do not accept the `options`
      kwarg at all) retries without the kwarg.
    """
    kwargs = dict(kwargs)

    opts = kwargs.get('options')
    if opts is not None and 'PATH_SUPPORTS_BLEND_RELATIVE' in set(opts):
        if not SUPPORTS_PATH_SUPPORTS_BLEND_RELATIVE:
            # make a copy and drop the unsupported option
            new_opts = set(opts) - {'PATH_SUPPORTS_BLEND_RELATIVE'}
            if new_opts:
                kwargs['options'] = new_opts
            else:
                kwargs.pop('options', None)

    from bpy.props import StringProperty as _bpy_StringProperty
    try:
        return _bpy_StringProperty(*args, **kwargs)
    except TypeError:
        # Older Blender may not accept the `options` kw at all
        kwargs.pop('options', None)
        return _bpy_StringProperty(*args, **kwargs)


def is_at_least(major: int, minor: int, patch: int = 0) -> bool:
    """Return True if running on at least the given Blender version."""
    return VERSION >= (major, minor, patch)


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name)
    except Exception:
        return default


def safe_get_by_path(root: Any, path: str, default: Any = None) -> Any:
    """Safely traverse a dotted attribute path returning default on failure.

    Example: safe_get_by_path(scene, "tool_settings.sculpt.unified_paint_settings")
    """
    cur = root
    for part in path.split('.'):
        if cur is None:
            return default
        cur = _safe_getattr(cur, part, default)
        if cur is default:
            return default
    return cur


# --- Paint compatibility -----------------------------------------------------------------

_MODE_MAP = {
    'WEIGHT_PAINT': 'weight_paint',
    'VERTEX_PAINT': 'vertex_paint',
    'SCULPT': 'sculpt',
    'IMAGE_PAINT': 'image_paint',
}


def get_unified_paint_settings(context: bpy.types.Context, mode: Optional[str] = None) -> Optional[Any]:
    """Return an object representing the unified_paint_settings for the current
    context in a version-agnostic way.

    If ``mode`` is provided it should be the Blender mode string (e.g. 'WEIGHT_PAINT').
    If not provided we infer it from ``context.mode``.

    Returns None if no unified paint settings object can be found.
    """
    scene = getattr(context, 'scene', None)
    if scene is None:
        return None

    # Prefer mode-specific substruct (Blender 5.0+)
    try:
        mode_key = mode or getattr(context, 'mode', None)
        if mode_key in _MODE_MAP:
            attr = _MODE_MAP[mode_key]
            # e.g. scene.tool_settings.sculpt.unified_paint_settings
            path = f"tool_settings.{attr}.unified_paint_settings"
            ups = safe_get_by_path(scene, path, default=None)
            if ups is not None:
                return ups
    except Exception:
        # fall through to older API
        pass

    # Fallback: older API used scene.tool_settings.unified_paint_settings
    ups = safe_get_by_path(scene, "tool_settings.unified_paint_settings", default=None)
    return ups


# --- UILayout helpers -------------------------------------------------------------------

def _sanitize_template_list_kwargs(kwargs: dict) -> dict:
    """Remove known-nonstandard/unsupported kwargs used historically by addons.

    Currently removes: 'sort_reverse', 'sort_lock'. Extend as required.
    """
    invalid = {'sort_reverse', 'sort_lock'}
    for key in list(kwargs.keys()):
        if key in invalid:
            kwargs.pop(key, None)
    return kwargs


def template_list(layout: bpy.types.UILayout, *args, **kwargs) -> Any:
    """Wrapper around ``UILayout.template_list`` that strips unsupported kwargs
    and falls back gracefully if the call fails.

    Usage matches ``UILayout.template_list``; this wrapper only sanitizes kwargs
    known to cause issues across versions.
    """
    kwargs = dict(kwargs)
    kwargs = _sanitize_template_list_kwargs(kwargs)

    try:
        return layout.template_list(*args, **kwargs)
    except TypeError:
        # Try calling with only positional args if some kwargs are not accepted
        try:
            return layout.template_list(*args)
        except Exception:
            # Give up silently and return None (caller should handle display)
            return None
    except Exception:
        return None


# grid_flow compatibility
def grid_flow(layout: bpy.types.UILayout, *args, **kwargs) -> bpy.types.UILayout:
    """Return a flow-like layout object.

    If ``layout.grid_flow`` is present (newer API) call and return it. Otherwise
    fall back to returning a row layout which is a reasonable substitute.
    """
    if hasattr(layout, 'grid_flow'):
        try:
            return layout.grid_flow(*args, **kwargs)
        except Exception:
            return layout.row()
    return layout.row()


# UIList / Grid support
def ui_list_supports_grid() -> bool:
    """Return whether the UIList layout_type enum still exposes GRID.

    This is used to guard code that checks ``self.layout_type in {'GRID'}``.
    """
    try:
        enum_items = bpy.types.UIList.bl_rna.properties['layout_type'].enum_items
        return any(getattr(it, 'identifier', None) == 'GRID' for it in enum_items)
    except Exception:
        return False


# UIList helpers (filtering / sorting) -----------------------------------------------------

def filter_items_compat(ui_list_instance: bpy.types.UIList, context: bpy.types.Context, data: Any, propname: str) -> Tuple[list, list]:
    """Compatibility wrapper to compute filter flags and sorting for a UIList.

    This mirrors the expected return from a UIList.filter_items method: a tuple
    (flags_list, sorting_list). The function attempts to use Blender helpers if
    available, otherwise returns a conservative default (no filtering, no sorting).
    """
    vgroups = getattr(data, propname, [])
    length = len(vgroups)

    # defaults
    flags = [ui_list_instance.bitflag_filter_item] * length
    sorting: list = []

    helper_funcs = getattr(bpy.types, 'UI_UL_list', None)

    try:
        # Filter by name if a filter is set
        if getattr(ui_list_instance, 'filter_name', None) and helper_funcs is not None:
            flags = helper_funcs.filter_items_by_name(ui_list_instance.filter_name, ui_list_instance.bitflag_filter_item, vgroups, "name", reverse=False)

        # Sorting helper: expect a list of (index, value) pairs; caller can compute value list
        # If the caller prepared such data, we can't know it; so it's best for callers
        # to compute the weight_averages as they see fit before calling this helper.
        # Here we attempt to use any provided sorting helper if present.
        if helper_funcs is not None and hasattr(helper_funcs, 'sort_items_helper'):
            # fall back to an unsorted list if no custom data is available
            sorting = []
    except Exception:
        # keep defaults
        pass

    return flags, sorting


# Exports
__all__ = [
    'VERSION', 'IS_5_0', 'is_at_least',
    'safe_get_by_path', 'get_unified_paint_settings',
    'template_list', 'grid_flow', 'ui_list_supports_grid', 'filter_items_compat',
    'SUPPORTS_PATH_SUPPORTS_BLEND_RELATIVE',
    'StringProperty',
]
