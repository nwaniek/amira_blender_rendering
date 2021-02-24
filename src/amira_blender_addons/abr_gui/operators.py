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
from . import utils
from . import properties

class AmiraOperatorImportConfiguration(bpy.types.Operator):
    bl_idname = "scene.abr_import_configuration"
    bl_label = "Import ABR Configuration"
    bl_options = {"REGISTER"}

    # tell the selection dialog that we want a file
    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH'
    )

    def execute(self, context):
        properties.config_to_blender(context, self.filepath, self.report)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class AmiraOperatorExportConfiguration(bpy.types.Operator):
    bl_idname = "scene.abr_export_configuration"
    bl_label = "Export ABR Configuration"
    bl_options = {"REGISTER"}

    # tell the selection dialog that we want a file
    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH'
    )

    def execute(self, context):
        config = properties.blender_to_config(context, self.report)
        utils.save_config_to_file(config, self.filepath, self.report)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



def invoke_generate_one(backend_scene):
    backend_scene.generate_one()


def invoke_generate_all(backend_scene):
    # TODO: call it. At the moment disabled for 'security' reasons to not
    # accidentally start rendering the entire dataset
    pass


def invoke_teardown(backend_scene):
    backend_scene.teardown()


class CallbackFacade:
    def __init__(self, context, report_fn, invoke_fn):
        self.context = context
        self.report_fn = report_fn
        self.invoke_fn = invoke_fn

    def __call__(self, module):
        """This callback will be invoked below via utils.import_backend_script.
        Its purpose is to check if the Scene Type is valid, and if yes,
        instantiate the backend script. This will then be forwarded to
        call_generate_one.
        """

        # get configuration
        config = properties.blender_to_config(self.context, self.report_fn)

        # instantiate user selected scene type
        scene_type_str = self.context.scene.abr_dataset_config.scene_type
        scene_class = getattr(module, scene_type_str)
        backend_scene = scene_class(config=config, interactive=True)

        # call generator function and then tear down everything again
        self.invoke_fn(backend_scene)
        invoke_teardown(backend_scene)

        # remove the backend object
        del backend_scene


class AmiraOperatorGenerateOne(bpy.types.Operator):
    bl_idname = "scene.abr_generate_one"
    bl_label = "Generate 1 (one) frame of the dataset"
    bl_description = "Generate a single frame of the dataset for the currently active camera\n"\
                     "NOTE: This might import and instantiate additional objects, depending on the settings for external objects and object instances."
    bl_options = {"REGISTER"}

    def execute(self, context):
        if not utils.try_import_abr(self.report):
            return
        else:
            from amira_blender_rendering.utils.io import expandpath

        file_path = expandpath(context.scene.abr_dataset_config.backend_script)
        if (file_path == '') or (not os.path.exists(file_path)):
            self.report({"ERROR"}, "Path to backend script required but empty or does not exist.")
        else:
            # Build a wrapper for the callback
            cb = CallbackFacade(context, self.report, invoke_generate_one)
            # now we attempt to import the backend module, which calls the callback
            # from above where we instantiate the scene
            utils.import_backend_script(file_path, cb)

        return {'FINISHED'}


class AmiraOperatorGenerateDataset(bpy.types.Operator):
    bl_idname = "scene.abr_generate_dataset"
    bl_label = "Generate entire dataset"
    bl_description = 'This generates the entire dataset.\n' \
                     'WARNING: Generating an entire dataset can take significant amounts of time. ' \
                     'It is recommended to render full datasets with abrgen'
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if not utils.try_import_abr(self.report):
            return
        else:
            from amira_blender_rendering.utils.io import expandpath

        file_path = expandpath(context.scene.abr_dataset_config.backend_script)
        if (file_path == '') or (not os.path.exists(file_path)):
            self.report({"ERROR"}, "Path to backend script required but empty or does not exist.")
        else:
            # Build a wrapper for the callback
            cb = CallbackFacade(context, self.report, invoke_generate_all)
            # now we attempt to import the backend module, which calls the callback
            # from above where we instantiate the scene
            utils.import_backend_script(file_path, cb)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class AmiraOperatorCleanupWorkspace(bpy.types.Operator):
    bl_idname = 'scene.abr_cleanup_workspace'
    bl_label = 'Clean up workspace'
    bl_description = 'Clean up workspace by removing all dynamically added objects'
    bl_options = {'REGISTER'}

    def execute(self, context):
        return {"FINISHED"}



class AmiraOperatorRebuildCompositorTree(bpy.types.Operator):
    # TODO: Make sure to call ABR's functions to avoid duplicate code!

    bl_idname = "nodes.abr_rebuild_compositor_tree"
    bl_label = "Rebuild ABR Compositor Tree"
    bl_options = {"REGISTER"}

    def _clean_tree(self, context):
        self.report({'INFO'}, "Removing all existing ABR compositor nodes")
        tree = context.scene.node_tree
        nodes = tree.nodes
        to_remove = list()
        for node in nodes:
            # we remove all nodes which have the abr_ prefix, as this is the identifier we use
            if node.name.startswith('abr_CN_'):
                nodes.remove(node)

    def _build_tree(self, context):
        self.report({'INFO'}, "Adding all compositor nodes required for ABR export")

        # TODO: collect all objects that are currently available in this blender file
        #       (excluding external objects) into the object list that we also use in
        #       ABR, then pass this to ABR's compositor node manager


        tree = context.scene.node_tree
        nodes = tree.nodes


        # NOTE: the following is taken with minor modifications from ABR/compositor_renderedobjects.py
        n_render_layers = nodes['Render Layers']

        # add file output node and setup format (16bit RGB without alpha channel)
        n_output_file = nodes.new('CompositorNodeOutputFile')
        n_output_file.name = 'abr_CN_RenderObjectsFileOutputNode'
        # n_output_file.base_path = self.path_base

        # the following format will be used for all sockets, except when setting a
        # socket's use_node_format to False (see range map as example)
        n_output_file.format.file_format = 'PNG'
        n_output_file.format.color_mode = 'RGB'
        n_output_file.format.color_depth = str(16)

        # setup sockets/slots. First is RGBA Image by default
        s_render = n_output_file.file_slots[0]
        s_render.use_node_format = True
        tree.links.new(n_render_layers.outputs['Image'], n_output_file.inputs['Image'])
        ##self.sockets['s_render'] = s_render

        # add all aditional file slots, e.g. depth map, image masks, backdrops, etc.
        # NOTE: blender Depth map is indeed a range map since it uses a perfect pinhole camera.
        #       That is, the map is not rectified yet.
        n_output_file.file_slots.new('Depth')
        s_depth_map = n_output_file.file_slots['Depth']
        s_depth_map.use_node_format = False
        s_depth_map.format.file_format = 'OPEN_EXR'
        s_depth_map.format.use_zbuffer = True
        tree.links.new(n_render_layers.outputs['Depth'], n_output_file.inputs['Depth'])
        ##self.sockets['s_depth_map'] = s_depth_map

        # backdrop setup (mask without any object)
        n_id_mask = nodes.new('CompositorNodeIDMask')
        n_id_mask.name = 'abr_CN_CompositorNodeIDMask_Backdrop'
        n_id_mask.label = 'ABR ID Mask Backdrop'
        n_id_mask.index = 0
        n_id_mask.use_antialiasing = True
        tree.links.new(n_render_layers.outputs['IndexOB'], n_id_mask.inputs['ID value'])

        mask_name = f"Backdrop"
        n_output_file.file_slots.new(mask_name)
        s_obj_mask = n_output_file.file_slots[mask_name]
        s_obj_mask.use_node_format = True
        tree.links.new(n_id_mask.outputs['Alpha'], n_output_file.inputs[mask_name])
        ##self.sockets['s_backdrop'] = s_obj_mask


        # TODO: this must be integrated with ABR implementation of collecting all objects.
        # collect all objects into a list
        objs = list()
        for o in bpy.data.objects:
            if not (o.type == 'MESH'):
                continue
            if not o.abr_object_config.track_object:
                continue
            objs.append(o)

        # go through all objects and link them to compute masks
        for i, obj in enumerate(objs):
            pass_index = i + 1337
            obj.pass_index = pass_index

            # mask setup
            n_id_mask = nodes.new('CompositorNodeIDMask')
            n_id_mask.index = pass_index
            n_id_mask.name = f'abr_CompositorNodeIDMask_obj{i}'
            n_id_mask.label = f'ABR ID Mask Object {obj.name}'
            n_id_mask.use_antialiasing = True
            tree.links.new(n_render_layers.outputs['IndexOB'], n_id_mask.inputs['ID value'])

            # new socket in file output
            mask_name = f"Mask{i:03}"
            n_output_file.file_slots.new(mask_name)
            s_obj_mask = n_output_file.file_slots[mask_name]
            s_obj_mask.use_node_format = True
            tree.links.new(n_id_mask.outputs['Alpha'], n_output_file.inputs[mask_name])


    def execute(self, context):
        if not context.scene.use_nodes:
            self.report({'WARNING'}, "Automatically enabling Use Nodes for this scene")
            context.scene.use_nodes = True

        if not context.scene.view_layers['View Layer'].use_pass_object_index:
            self.report({'WARNING'}, "Automatically enabling Object Indexes for View Layer")
            context.scene.view_layers['View Layer'].use_pass_object_index = True

        self._clean_tree(context)
        self._build_tree(context)

        return {'FINISHED'}


class AmiraOperatorExternalObjects(bpy.types.Operator):
    bl_idname = 'abr_external_objects.list_action'
    bl_label = 'External Object List Actions'
    bl_description = 'Move external objects up or down, add and remove'
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items = (
            ('UP', 'Up', ''),      # TODO: implement
            ('DOWN', 'Down', ''),  # TODO: implement
            ('ADD', 'Add', ''),
            ('REMOVE', 'Remove', '')
        )
    )

    def invoke(self, context, event):
        # try to get the item we're working on
        scn = context.scene
        idx = scn.abr_external_objects_index
        try:
            item = scn.abr_external_objects[idx]
        except IndexError:
            pass
        else:
            if self.action == 'REMOVE':
                scn.abr_external_objects.remove(idx)
                if (idx == 0):
                    if len(scn.abr_external_objects) > 0:
                        scn.abr_external_objects_index = 0
                    else:
                        scn.abr_external_objects_index = -1
                else:
                    scn.abr_external_objects_index = idx-1

                self.report({'INFO'}, f"Removed external item {idx}")

        if self.action == 'ADD':
            item = scn.abr_external_objects.add()
            item.id = len(scn.abr_external_objects)
            item.file_type = 'BLEND'
            item.file_path = ''
            item.scale = 1.0
            # TODO: assign a new name with .xyz numbering similar to how Blender names other objects
            item.name = 'ExternalObject'
            scn.abr_external_objects_index = (len(scn.abr_external_objects)-1)
            self.report({'INFO'}, "Added external item")

        return {'FINISHED'}




classes = (
    # operators
      AmiraOperatorRebuildCompositorTree
    , AmiraOperatorImportConfiguration
    , AmiraOperatorExportConfiguration
    , AmiraOperatorGenerateOne
    , AmiraOperatorGenerateDataset
    , AmiraOperatorExternalObjects
    , AmiraOperatorCleanupWorkspace
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
