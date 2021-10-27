# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "mgto_tools_blender",
    "author" : "Till 'rollin' Maginot",
    "description" : "Various tools and macros for modelling, skinning, rigging, animation and export",
    "blender" : (2, 80, 0),
    "version" : (0, 6, 17), # check also version in 'About' panel
    "location" : "View3D Panel",
    "warning" : "Might be unstable",
    "category" : "Generic"
}


# Import or reload submodules #########################################################

# if "bpy" in locals():
#     import importlib
#     importlib.reload(props)
#     importlib.reload(overlays_manager)
#     importlib.reload(panels)
#     importlib.reload(skin_op_weights)
#     importlib.reload(test_op)
#     importlib.reload(update_addon)
# else:
#     from . import props
#     from . import overlays_manager
#     from . import panels
#     from . import skin_op_weights
#     from . import test_op
#     from . import update_addon

from . mgtools_manager_overlays import MGTOOLSOverlayManager

# Import #########################################################

import bpy


# Register #########################################################

# we use auto_load now -----------------------------------------------
# from . props import MGTOOLS_properties
# from . overlays_manager import MGTOOLSOverlayManager
# from . panels import MGTOOLS_PT_weighting, MGTOOLS_PT_sandbox, MGTOOLS_PT_about
# from . skin_op_weights import MGTOOLS_OT_weighting_show_weights, MGTOOLS_OT_weighting_hide_weights, MGTOOLS_OT_weighting_set_weights, MGTOOLS_OT_weighting_add_weights
# from . test_op import MGTOOLS_OT_sandbox_debug1
# classes = (
#     MGTOOLS_properties,
#     MGTOOLS_PT_weighting,
#     MGTOOLS_PT_sandbox,
#     MGTOOLS_PT_about,
#     MGTOOLS_OT_sandbox_debug1, 
#     MGTOOLS_OT_weighting_show_weights, MGTOOLS_OT_weighting_hide_weights,
#     MGTOOLS_OT_weighting_set_weights, MGTOOLS_OT_weighting_add_weights
#     )
# def register():
#     for cls in classes:
#         bpy.utils.register_class(cls)
# def unregister():
#     MGTOOLSOverlayManager.deinit()
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)
# ------------------------------------------------------------------ 

from . import auto_load
auto_load.init()

def register():
    try:
        auto_load.register()
    except:
        traceback.print_exc()

def unregister():
    MGTOOLSOverlayManager.deinit()
    try:
        auto_load.unregister()
    except: 
        traceback.print_exc()


# Helper #########################################################

def debug_mode():
    # return True
    return (bpy.app.debug_value != 0)