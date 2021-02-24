#!/usr/bin/env python

# Copyright (c) 2020 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# <https://github.com/boschresearch/amira-blender-rendering>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


bl_info = {
    "name"        : "AMIRA Blender Rendering GUI Add-on",
    "author"      : "The AMIRA Team of the Bosch Center for Artificial Intelligence",
    "version"     : (0, 1),
    "blender"     : (2, 80, 0),
    "location"    : "Everywhere!",
    "description" : "Collection of tools for dataset generation with ABR (AMIRA Blender Rendering).",
    "warning"     : "",
    "wiki_url"    : "",
    "category"    : "Interface",
}


if "bpy" in locals():
    import importlib
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(gui)
    importlib.reload(utils)
    importlib.reload(preferences)
else:
    import bpy
    from . import properties
    from . import operators
    from . import gui
    from . import utils
    from . import preferences


def register():
    properties.register()
    operators.register()
    gui.register()
    preferences.register()


def unregister():
    properties.unregister()
    operators.unregister()
    gui.unregister()
    preferences.unregister()

