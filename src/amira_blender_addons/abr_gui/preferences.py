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

import bpy
from os.path import basename, dirname

class AmiraAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    abr_path: bpy.props.StringProperty(
        name='Path to AMIRA Blender Rendering (abr)',
        default='',
        subtype='DIR_PATH'
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'abr_path')


def register():
    bpy.utils.register_class(AmiraAddonPreferences)

def unregister():
    bpy.utils.unregister_class(AmiraAddonPreferences)
