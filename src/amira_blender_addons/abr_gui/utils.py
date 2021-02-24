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
import os
import sys
import pathlib
import importlib
import inspect
from . import messages


def try_import_abr(report_fn=None, reload=False):
    # get the path to abr, which can be set in the addon preferences
    prefs = bpy.context.preferences
    addon_prefs = prefs.addons[__package__].preferences
    abr_path = addon_prefs.abr_path
    if abr_path == '':
        if report_fn:
            report_fn({'ERROR'}, messages.msg_abr_import_error)
        else:
            print(messages.msg_abr_import_error)
        return False

    # add to system path, then import
    if abr_path not in sys.path:
        sys.path.append(abr_path)
    import amira_blender_rendering
    # (reload) the most common modules from ABR
    if reload:
        for m_str in ['amira_blender_rendering', 'amira_blender_rendering.datastructures']:
            if m_str in sys.modules:
                importlib.reload(sys.modules[m_str])
    return True


def import_backend_script(file_path, callback):
    # NOTE: The directory with the backend script MUST be on the search
    #       path. This must be documented very well to inform users so that
    #       they don't mess around with their paths and produce entire modules
    #       in there.
    path = pathlib.Path(file_path)
    dir_str = str(path.parent)
    dir_added = False
    if dir_str not in sys.path:
        sys.path.append(dir_str)
        dir_added = True

    module_name = path.stem
    # import and reload to avoid getting a stale module
    # TODO: error checking
    module = importlib.import_module(module_name)
    # TODO: even despite reload, extracting the scene types might be out of sync!
    importlib.reload(module)

    # call backend, if passed in
    if callback:
        callback(module)

    # get rid of the module again, and tidy up the path if necessary
    del module
    if dir_added:
        sys.path.remove(dir_str)


def save_config_to_file(config, filepath, report_fn=None):
    """Save a Configuration object to a path"""
    with open(filepath, 'w') as txt_file:
        txt_file.write(config.to_cfg())
    if report_fn:
        report_fn({'INFO'}, f"Saved ABR Configuration to {filepath}.")
