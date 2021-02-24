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
from . import utils
from . import operators

# TODO: maybe merge this with the Scene Setup
class AmiraPanelDatasetConfiguration(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_dataset_configuration'
    bl_label = "Global Configuration"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        col = self.layout.column()
        dataset_config = context.scene.abr_dataset_config
        col.prop(dataset_config, 'image_count')
        col.prop(dataset_config, 'base_path', text='Output Path')
        col.prop(dataset_config, 'backend_script', text='Backend Script')
        col.prop(dataset_config, 'scene_type', text='Scene Type')

    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='WORLD')


class AmiraPanelImportExport(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_import_export'
    bl_label = "Config Import / Export"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # We might want to nest this within the dataset configuration panel
    #bl_parent_id = 'AMIRA_PT_dataset_configuration'

    def draw(self, context):
        self.layout.operator('scene.abr_import_configuration', icon='IMPORT')
        self.layout.operator('scene.abr_export_configuration', icon='EXPORT')

    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='FILE')
        pass



class AmiraULExternalObjects(bpy.types.UIList):
    bl_idname = 'AMIRA_UL_external_objects'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.8)
            split.label(text=f'{item.name}:{item.count}', icon='OBJECT_DATAMODE')
            #split.prop(item, 'enabled', text='', emboss=True)

        elif self.layout_type == {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon_value=layout.icon(0))

    def invoke(self, context, event):
        pass


class AmiraPanelExternalObjects(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_external_objects'
    bl_label = 'External Objects'
    bl_category = 'AMIRA'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row()
        row.template_list(
            'AMIRA_UL_external_objects', '',
            scn, 'abr_external_objects',
            scn, 'abr_external_objects_index',
            rows=2)

        col = row.column(align=True)
        col.operator('abr_external_objects.list_action', icon='ADD', text='').action = 'ADD'
        col.operator('abr_external_objects.list_action', icon='REMOVE', text='').action = 'REMOVE'

        idx = scn.abr_external_objects_index
        if idx < 0:
            return
        try:
            item = scn.abr_external_objects[idx]
        except IndexError:
            return

        layout.separator()
        layout.prop(item, 'name')
        layout.prop(item, 'file_path')

        split = layout.split()
        split.prop(item, 'scale', text='Scale')
        split.prop(item, 'count', text='Instances')
        # split.prop(item, 'enabled', text='active')


    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='OBJECT_HIDDEN')


class AmiraPanelDatasetGeneration(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_dataset_generation'
    bl_label = "Dataset Generation & Tools"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        col = self.layout.column()
        col.operator('scene.abr_generate_one')
        col.operator('scene.abr_generate_dataset')


    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='RENDER_RESULT')


class AmiraPanelDatasetTools(bpy.types.Panel):
    bl_idname = "AMIRA_PT_dataset_tools"
    bl_label = "Tools"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "AMIRA_PT_dataset_generation"

    def draw(self, context):
        layout = self.layout
        layout.operator(operators.AmiraOperatorCleanupWorkspace.bl_idname)

    def draw_header(self, context):
        #layout = self.layout.column(align=True)
        #layout.label(text='', icon='TOOL_SETTINGS')
        pass


class AmiraPanelCompositor(bpy.types.Panel):
    bl_idname = "AMIRA_PT_compositor"
    bl_label = "AMIRA compositor"
    bl_category = "AMIRA"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator('nodes.abr_rebuild_compositor_tree')

    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='NODE_COMPOSITING')


# TODO: this panel is currently not registered!
class AmiraPanelObjectProperties(bpy.types.Panel):
    bl_idname = "OBJECT_PT_amira_object_properties"
    bl_label = "AMIRA Object Properties"
    bl_category = "AMIRA"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def _props_mesh(self, context):
        row = self.layout.row()
        row.prop(context.object, "abr_object_config.track_object")

    def _props_camera(self, context):
        row = self.layout.row()
        row.prop(context.object, "abr_camera_config.use_camera")

    def draw(self, context):
        if not context.object:
            return
        _fn_map = { 'MESH':   self._props_mesh
                  , 'CAMERA': self._props_camera
                  }
        if not context.object.type in _fn_map:
            return
        _fn_map[context.object.type](context)


def make_caminfo_panel(context, layout, cam_info):
    col = layout.column(align=True)
    split = col.split(factor=0.3)
    split.label(text='Resolution X')
    split.prop(cam_info, 'width', text='')
    split = col.split(factor=0.3)
    split.label(text='Resolution Y')
    split.prop(cam_info, 'height', text='')

    split = col.split(factor=0.3)
    split.label(text='Model Name')
    split.prop(cam_info, 'model', text='')

    layout.separator()

    intrinsics = cam_info.intrinsics
    box = layout.box()
    col = box.column(align=True)
    col.prop(intrinsics, "use_intrinsics", text='Use camera intrinsics')
    split = col.split()
    col = split.column(align=True)
    col.prop(intrinsics, 'fx')
    col.prop(intrinsics, 'fy')
    col.enabled = intrinsics.use_intrinsics
    col = split.column(align=True)
    col.prop(intrinsics, 'cx')
    col.prop(intrinsics, 'cy')
    col.enabled = intrinsics.use_intrinsics

    # TODO: maybe remove zeroing from GUI, or even remove it from the config alltogether
    zeroing = cam_info.zeroing
    box = layout.box()
    col = box.column(align=True)
    col.label(text='Camera Zeroing')
    row = col.row(align=True)
    row.prop(zeroing, 'zero_x', text='X')
    row.prop(zeroing, 'zero_y', text='Y')
    row.prop(zeroing, 'zero_z', text='Z')


class AmiraPanelDefaultCameraSetup(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_default_camera_setup'
    bl_label = "Global Camera Setup"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout.column(align=True)
        cam_info = context.scene.abr_camera_config
        make_caminfo_panel(context, layout, cam_info)


    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='CAMERA_DATA')
        return


class AmiraPanelSceneSetup(bpy.types.Panel):
    bl_idname = 'AMIRA_PT_scene_setup'
    bl_label = "Scene & Render Setup"
    bl_category = "AMIRA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scene_config = context.scene.abr_scene_config
        col = self.layout.column(align=True)
        col.prop(scene_config, 'forward_frames')
        col.prop(scene_config, 'environment_texture')
        col.prop(scene_config, 'blend_file')

        # TODO: use proper grid layout
        render_setup = context.scene.abr_render_setup_config
        self.layout.separator()
        col = self.layout.column(align=True)
        col.prop(render_setup, 'backend')
        col.prop(render_setup, 'integrator')
        split = col.split(factor=0.235)
        split.label(text='Samples')
        split.prop(render_setup, 'samples', text='')
        split = col.split(factor=0.235)
        split.label(text='Denoising')
        split.prop(render_setup, 'denoising', text='Enable Denoising')
        split = col.split(factor=0.235)
        split.label(text='Occlusions')
        split.prop(render_setup, 'allow_occlusions', text='Allow Occlusions')

    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='SCENE_DATA')



class AmiraPanelObjectInformation(bpy.types.Panel):
    bl_idname = "OBJECT_PT_amira_tools_object_information"

    # label of the tool / caption
    bl_label = "Object Configuration"
    # restrict visibility of the panel to object mode
    bl_context = "objectmode"
    # category name (which is the name/label on the tab)
    bl_category = "AMIRA"
    # restrict to which view
    bl_space_type = "VIEW_3D"
    # where to find it
    bl_region_type = "UI"

    def draw(self, context):
        if context.object is None:
            return

        layout = self.layout.column(align=True)

        if context.object.type == 'MESH':
            layout.prop(context.object.abr_object_config, "track_object")
            if context.object.abr_object_config.track_object:
                layout.prop(context.object.abr_object_config, 'instance_count')

        elif context.object.type == 'CAMERA':
            # use this camera?
            layout.prop(context.object.abr_camera_config, "use_camera")

            cam_info = context.object.abr_camera_config
            if not cam_info.use_camera:
                return

            layout.prop(cam_info, 'use_custom_configuration')
            if not cam_info.use_custom_configuration:
                return

            make_caminfo_panel(context, layout, cam_info)

    @classmethod
    def poll(cls, context):
        # this method can be used to hide panels if certain objects are not selected
        # or invalid for what we're doing
        return (context.object is not None) and (context.object.type in ['MESH', 'CAMERA'])


    def draw_header(self, context):
        layout = self.layout.column(align=True)
        layout.label(text='', icon='OBJECT_DATA')



classes = (
    # panels and other GUI items
      AmiraPanelImportExport
    , AmiraPanelDatasetConfiguration
    , AmiraPanelSceneSetup
    , AmiraPanelDefaultCameraSetup
    , AmiraPanelObjectInformation
    , AmiraPanelDatasetGeneration
    , AmiraPanelDatasetTools
    , AmiraULExternalObjects
    , AmiraPanelExternalObjects
    , AmiraPanelCompositor
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
