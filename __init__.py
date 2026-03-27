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
    "description" : "Various tools and macros for modelling, skinning, rigging, animation and export.",
    "blender" : (2, 80, 0),
    "version" : (0, 6, 29), # check also version in 'About' panel
    "location" : "View3D Panel",
    "warning" : "Might be unstable",
    "category" : "Generic"
}


# Import or reload submodules #########################################################

from . mgtools_manager_overlays import MGTOOLSOverlayManager

# Import #########################################################

import bpy
import traceback


# Register #########################################################

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