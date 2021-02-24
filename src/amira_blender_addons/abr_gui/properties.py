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
import inspect
from . import utils
from . import messages

# NOTE: we will import some classes and methods below within the functions. The
#       reason for this is that a user must specify the path to the ABR Core,
#       and only with this path, we will succeed to import from ABR.


def _abr_import_error_msg(self, context):
    self.layout.label(text=messages.msg_abr_import_error)

class StringValue(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(name='Value', default='')


class AmiraDatasetConfiguration(bpy.types.PropertyGroup):

    # helper function to get the list of items for scene_types from available_scene_types.
    # the latter will be updated on changing the path to the backend script, while
    # the enum is computed during draw of the corresponding UI element - hence this
    # "two stage" approach
    def _get_scene_types(self, context):
        config = context.scene.abr_dataset_config
        enum_items = list()
        for scene_type in config.available_scene_types:
            enum_items.append((scene_type.value, scene_type.value, ''))
        return enum_items


    def _update_dataset_config_backend_script(self, context):
        # TODO: the following code with the callback would allow to specify
        #       multiple different scene types within one backend script. At
        #       the moment, we do not support this from within abrgen, but it
        #       might be quite handy to have this possibility.

        scene_types = list()

        def _cb_backend(backend):
            from amira_blender_rendering.interfaces import ABRScene
            classes = inspect.getmembers(backend, inspect.isclass)
            scene_types.clear()
            for i, cls in enumerate(classes):
                if issubclass(cls[1], ABRScene):
                    cls_name = cls[1].__name__
                    scene_types.append(cls_name)

        # clear the configuration
        config = context.scene.abr_dataset_config
        config.available_scene_types.clear()

        # attempt to load the backend script and find all possible SceneTypes within the script
        # get the path and load the module.
        if not utils.try_import_abr():
            # show error message to the user
            bpy.context.window_manager.popup_menu(_abr_import_error_msg, title="Error", icon='ERROR')
            return
        from amira_blender_rendering.utils.io import expandpath

        file_path = expandpath(self.backend_script)
        if os.path.exists(file_path):
            utils.import_backend_script(file_path, _cb_backend)

            # update the configuration
            for scene in scene_types:
                name = config.available_scene_types.add()
                name.value = scene

    image_count: bpy.props.IntProperty(
        name='Image Count',
        default=1,
        min=1
    )

    base_path: bpy.props.StringProperty(
        name='Dataset Output Base Path',
        default='',
        subtype='DIR_PATH'
    )

    backend_script: bpy.props.StringProperty(
        name='Scene Backend Script',
        default='',
        subtype='FILE_PATH',
        update=_update_dataset_config_backend_script
    )

    # make this restricted to an enum, so that users cannot manually change this
    scene_type: bpy.props.EnumProperty(
        items=_get_scene_types,
        name="Available Scene Types"
    )
    # for this to work, we need to somehow collect a list of strings, though.
    available_scene_types: bpy.props.CollectionProperty(type=StringValue)


    def to_config(self, config):
        """Store all elements of the PropertyGroup to config, where config
        is an instance of ABR Configuration. Note that this will overwrite values
        in config.

        Args:
            config(Configuration): Configuration instance containing the ABR configuration.
        """

        # XXX: assume config is the config.dataset namespace
        config.image_count = int(self.image_count)
        config.base_path   = self.base_path

        if len(self.available_scene_types) > 0:
            config.scene_type = self.scene_type
        else:
            config.scene_type = ''


    def from_config(self, config):
        """Read settings from `config` and store them in the PropertyGroup"""

        # XXX: assume config is the config.dataset namespace

        self.image_count    = config.get('image_count', 1)
        self.base_path      = config.get('base_path', '')
        self.backend_script = config.get('backend_script', '')
        try:
            self.scene_type = config.get('scene_type', '')
        except TypeError:
            pass

# $HOME/amira/amira_blender_rendering/scenes/basic_scene.py



class AmiraSceneConfiguration(bpy.types.PropertyGroup):
    environment_texture: bpy.props.StringProperty(
        name='Environment Textures',
        description='Path to specific environment texture or to a directory containing textures',
        default='',
        subtype='DIR_PATH'
    )
    forward_frames: bpy.props.IntProperty(
        name='Forward frames',
        description='Number of frames to forward-simulate for physics, e.g. to simualte objects falling onto a surface',
        default=1,
        min=0
    )
    blend_file: bpy.props.StringProperty(
        name='Blender File',
        description='Specify path where the Blender file can be located.\n' \
                    'NOTE: This is not required for interactive debugging, but will be required when using abrgen to generate datasets',
        default='',
       subtype='FILE_PATH',
    )

    # TODO: cameras, num_frames, num_camera_locations

    def to_config(self, config):
        # XXX: assume config is config.scene_setup
        config.blend_file = self.blend_file
        config.environment_texture = self.environment_texture
        config.forward_frames = self.forward_frames

    def from_config(self, config):
        # XXX: assume config is config.scene_setup
        self.blend_file = config.get('blend_file', '')
        self.environment_texture = config.get('environment_texture', '')
        self.forward_frames = int(config.get('forward_frames', 0))


class AmiraRenderSetup(bpy.types.PropertyGroup):
    backend: bpy.props.EnumProperty(
        name='Render Backend',
        description='Render Backend Configuration',
        items=[
            ('blender-cycles', 'blender-cycles', '') ,
        ]
    )
    integrator: bpy.props.EnumProperty(
        name='Integrator',
        description='Integrator to use during rendering',
        items=[
            ('BRANCHED_PATH', 'BRANCHED_PATH', ''),
            ('PATH', 'PATH', ''),
        ]
    )
    denoising: bpy.props.BoolProperty(
        name='Enable Denoising',
        description='Use denoising methods during rendering',
        default=True,
    )
    samples: bpy.props.IntProperty(
        name='Samples',
        description='Path tracer samples per pixel during dataset rendering',
        default=64,
        min=1
    )
    allow_occlusions: bpy.props.BoolProperty(
        name='Allow Occlusions',
        description='Allow occlusions during dataset rendering',
        default=False,
    )


    def to_config(self, config):
        # assumes that config is the render_setup namespace
        config.backend = self.backend
        config.integrator = self.integrator
        config.denoising = self.denoising
        config.samples = self.samples
        config.allow_occlusions = self.allow_occlusions


    def from_config(self, config):
        # try to import strbool from ABR
        if not utils.try_import_abr():
            bpy.context.window_manager.popup_menu(_abr_import_error_msg, title="Error", icon='ERROR')
            return
        from amira_blender_rendering.datastructures import strbool

        self.backend = config.backend
        self.integrator = config.integrator
        if isinstance(config.denoising, str):
            self.denoising = strbool(config.denoising)
        else:
            self.denoising = config.denoising
        self.samples = int(config.samples)
        if isinstance(config.allow_occlusions, str):
            self.allow_occlusions = strbool(config.allow_occlusions)
        else:
            self.allow_occlusions = config.allow_occlusions



class AmiraCameraIntrinsics(bpy.types.PropertyGroup):
    use_intrinsics: bpy.props.BoolProperty(
        name='Use intrinsics',
        default=False)
    fx: bpy.props.FloatProperty(name="fx")
    fy: bpy.props.FloatProperty(name="fy")
    cx: bpy.props.FloatProperty(name="cx")
    cy: bpy.props.FloatProperty(name="cy")


class AmiraCameraZeroing(bpy.types.PropertyGroup):
    zero_x: bpy.props.FloatProperty(name="zero x", default=0.0)
    zero_y: bpy.props.FloatProperty(name="zero y", default=0.0)
    zero_z: bpy.props.FloatProperty(name="zero z", default=0.0)


class AmiraCameraConfiguration(bpy.types.PropertyGroup):
    use_camera: bpy.props.BoolProperty(
        name = "Generate dataset for camera",
        description = "Use this camera for dataset generation",
        default=False
    )
    use_custom_configuration: bpy.props.BoolProperty(
        name = "Use Custom Configuration",
        description = "Use custom instead of global camera configuration",
        default=False,
    )
    model: bpy.props.StringProperty(
        name = "Camera Model",
        description = "Camer Model name, mostly for documentation purposes",
        default = "pinhole",
    )
    width: bpy.props.IntProperty(
        name = 'Resolution X',
        description = 'Width of the image procuded by the camera',
        default = 800,
    )
    height: bpy.props.IntProperty(
        name = 'Resolution Y',
        description = 'Height of the image produced by the camera',
        default = 600,
    )
    zeroing: bpy.props.PointerProperty(type=AmiraCameraZeroing)
    intrinsics: bpy.props.PointerProperty(type=AmiraCameraIntrinsics)


    def from_config(self, config):
        # try to import strbool
        if not utils.try_import_abr():
            bpy.context.window_manager.popup_menu(_abr_import_error_msg, title="Error", icon='ERROR')
            return
        from amira_blender_rendering.datastructures import strbool

        # note: this is used for specific cameras as well as for global settings
        # TODO: change the behavior of use_camera. (see comment below in scan_cameras)
        self.use_camera = config.get('use_camera', False)
        self.model = config.get('model', '')

        # we have 'use_intrinsics', hence this should be a valid camera
        # configuration section. Now we figure out if there's a custom
        # config. At the moment, this is not properly mapped in the
        # configuration, which is why we have this ugliness here
        has_custom_config = ('width' in config) or ('height' in config) or strbool(config['use_intrinsics'])
        self.use_custom_configuration = has_custom_config
        self.width = int(config.get('width', 0))
        self.height = int(config.get('height', 0))

        zeroing = config.get('zeroing', None)
        if zeroing and len(zeroing) > 0:
            self.zeroing.zero_x = float(zeroing[0])
            self.zeroing.zero_y = float(zeroing[1])
            self.zeroing.zero_z = float(zeroing[2])
        else:
            self.zeroing.zero_x = 0.0
            self.zeroing.zero_y = 0.0
            self.zeroing.zero_z = 0.0

        # TODO: change intrinsic in config to intrinsics ?
        use_intrinsics = config.get('use_intrinsics', True)
        if type(use_intrinsics) == str:
            self.intrinsics.use_intrinsics = strbool(use_intrinsics)
        else:
            self.intrinsics.use_intrinsics = use_intrinsics

        intrinsics = config.get('intrinsics', list())
        # convert string to list in case we got a string
        if type(intrinsics) == str:
            intrinsics = intrinsics.split(',')
        if len(intrinsics) > 0:

            self.intrinsics.fx = float(intrinsics[0])
            self.intrinsics.fy = float(intrinsics[1])
            self.intrinsics.cx = float(intrinsics[2])
            self.intrinsics.cy = float(intrinsics[3])
        else:
            self.intrinsics.fx = 0.0
            self.intrinsics.fy = 0.0
            self.intrinsics.cx = 0.0
            self.intrinsics.cy = 0.0

    def to_config(self, config):
        # note: config assumed to be a camera_info-suitable namespace
        # the write_use_camera flag is required
        config.model = self.model
        config.width = self.width
        config.height = self.height
        config.zeroing = [self.zeroing.zero_x, self.zeroing.zero_y, self.zeroing.zero_z]
        # TODO: change intrinsic to intrinsics in ABR's configurations
        config.use_intrinsics = self.intrinsics.use_intrinsics
        config.intrinsics = [self.intrinsics.fx, self.intrinsics.fy, self.intrinsics.cx, self.intrinsics.cy]



class AmiraObjectConfiguration(bpy.types.PropertyGroup):
    # Mesh specific properties
    track_object: bpy.props.BoolProperty(
        name = "Generate data for object",
        description = "Track object and generate dataset for it",
        default=False
    )
    # number of instances for this object
    instance_count: bpy.props.IntProperty(
        name = 'Instance count',
        description = 'Determine number of instance of this object to dynamically create for dataset',
        default=1,
        min=1
    )
    # was this object imported automatically by ABR for debugging / dataset generation purposes?
    is_instantiated_object: bpy.props.BoolProperty(
        name = 'Dynamically added object',
        description = 'Identify if this object was dynamically added, e.g. it was imported for dataset generation from an external file, or instantiated from another object',
        default=False
    )


class AmiraExternalObject(bpy.types.PropertyGroup):
    file_path: bpy.props.StringProperty(
        name='File Path',
        description='Path to the file of the object',
        default='',
        subtype='FILE_PATH',
    )
    scale: bpy.props.FloatProperty(
        name='Object Scale',
        description='Scale Information of the object',
        default=1.0,
    )
    # TODO: this field name is inconsistent with AmiraObjectConfiguration
    count: bpy.props.IntProperty(
        name='Instance Count',
        description='Number of instances for dataset generation',
        default=1,
        min=0,
    )
    name: bpy.props.StringProperty(
        name='Object Name',
        description='Name used to identify object',
        default='',
    )

    def from_config(config):
        pass

    def to_config(config):
        pass




def untrack_objects(context):
    """Untrack all objects, i.e. disable data generation."""
    for obj in bpy.data.objects:
        # exclude cameras
        if not obj.type == 'MESH':
            continue
        if hasattr(obj, 'abr_object_config'):
            obj.abr_object_config.track_object = False
            obj.abr_object_config.instance_count = 0


def untrack_cameras(context):
    """Untrack all cameras (i.e. disable dataset generation) and return a dict
    of all available cameras."""
    cameras = dict()
    for obj in bpy.data.objects:
        if not obj.type == 'CAMERA':
            continue
        else:
            cameras[obj.name] = obj
            if hasattr(obj, 'abr_camera_config'):
                obj.abr_camera_config.use_camera = False
                obj.abr_camera_config.use_custom_configuration = False
    return cameras


def scan_targets(context, config, report_fn):
    # try to import abr, because we'll need the Configuration class
    if not utils.try_import_abr(report_fn):
        return
    from amira_blender_rendering.datastructures import Configuration

    # import all part definitions as external objects.
    # NOTE: This can handle a new format for storing object information in the
    #       config, as well as the old format
    #       The new (improved) format is:
    #            part_name.file_path = /path/to/file
    #            part_name.name      = name_of_part_within_file (can be ommitted)
    #            part_name.scale     = scaling_factor

    # TODO: is it possible to move this into the object propertygroup above?
    context.scene.abr_external_objects_index = -1
    context.scene.abr_external_objects.clear()

    # list of external target objects
    external_targets = dict()
    # list of internal target objects
    internal_targets = dict()
    # list of all target objects, including the ones within the current blender file
    all_targets = [v.strip() for v in config.scenario_setup.target_objects.split(',')]
    for target in all_targets:
        if not target.startswith('parts.'):
            name, count = target.split(':')
            internal_targets[name] = int(count)
        else:
            # this is a real external object, so let's get some information about it
            name, count = target[6:].split(':')
            external_targets[name] = int(count)

    # details of all external parts
    uses_old_style_config = False
    for itm in config.parts:
        # determine if this is an old-style or new-style configuration
        if isinstance(config.parts[itm], Configuration):
            # NEW style configuration
            # add new object to the collection
            obj = context.scene.abr_external_objects.add()
            # new style
            obj.name = config.parts[itm].get('name', itm)
            obj.file_path = config.parts[itm].get('file_path', '')
            obj.scale = float(config.parts[itm].get('scale', 1.0))
        else:
            # OLD style configuration
            uses_old_style_config = True
            special_keys = ['ply', 'ply_scale']
            if itm in special_keys:
                continue
            obj = context.scene.abr_external_objects.add()
            obj.name = itm
            obj.file_path = config.parts[itm]
            obj.scale = float(config.parts.ply_scale.get('itm', 1.0))

        if obj.name in external_targets:
            obj.count = external_targets[obj.name]
        else:
            report_fn({'WARNING'}, f"name {obj.name} not found in {external_targets}.")
            obj.count = 0

    # inform the user about old-style configs
    if uses_old_style_config:
        report_fn({'INFO'}, f'Configuration file "{self.filepath}" contains old-style configuration for part declarations.\n'
                               'Recommendation: Update the configuration to new-style configurations.')

    # first go through all objects and set tracking to off
    untrack_objects(context)

    # go through all internal targets and set up accordingly
    missing_targets = list()
    for target in internal_targets:
        if target not in bpy.data.objects:
            missing_targets.append(target)
        else:
            obj = bpy.data.objects[target]
            obj.abr_object_config.instance_count = internal_targets[target]
            obj.abr_object_config.track_object = internal_targets[target] > 0

    # if there are targets missing in the blender file, inform the user
    if len(missing_targets) > 0:
        warn_str = f'The following target objects, specified in {self.filepath}, were not found: '
        for target in missing_targets:
            warn_str = warn_str + f'\n{target}'
        report_fn({'WARNING'}, warn_str)



def scan_cameras(context, config, report_fn):
    """This function scans for all cameras specified in the Configuration object
    and sets them up accordingly."""

    # try to import dict_get_nested
    if not utils.try_import_abr(report_fn):
        return
    from amira_blender_rendering.datastructures import dict_get_nested

    # TODO: at the moment, camera_info sections for cameras which are not
    # enabled will not be read from the configuration!

    # reset knowledge cameras, this also returns a list of all cams
    cameras = untrack_cameras(context)

    # get a list of all cameras that are enabled for rendering
    enabled_cameras = config.scene_setup.cameras
    if isinstance(enabled_cameras, str):
        enabled_cameras = [c.strip() for c in enabled_cameras.split(',')]
    elif not isinstance(enabled_cameras, list):
        report_fn({'ERROR'}, "config.scene_config.cameras is not of type string or list!")
        return

    # find out which cameras to enable, and how to enable them
    for cam_str in enabled_cameras:
        report_fn({'INFO'}, f"Checking camera config for {cam_str}.")

        # determine if the camera is available within blender, or not
        if cam_str not in cameras:
            report_fn({'WARNING'}, f"Camera {cam_str} specified in configuration, but not found in blender file!")
            continue

        cam = cameras[cam_str]
        cam.abr_camera_config.use_camera = True

        # determine if we have a specific camera_info setup.
        # NOTE: this is very tricky. A camera with the name 'Camera.001' (or any
        # camera with a . in its name) induces a Configuration object
        # `camera_info.Camera.001`, for which the following `if` will succeed!
        # Hence, we will check if use_intrinsics is available. If not, then this
        # is not a valid camera_info Configuration
        try:
            cam_cfg = config.camera_info[cam_str]
        except:
            report_fn({'ERROR'}, f"Could not read configuration for camera {cam_str}")
        else:
            if 'use_intrinsics' in cam_cfg:
                # use the PropertyGroup for loading
                cam.abr_camera_config.from_config(cam_cfg)
                # Set use_camera again, as from_config defaults it to 0
                # TODO: adapt from_config to not set use_camera to 0
                cam.abr_camera_config.use_camera = True



def external_objects_to_config(context, config):
    """Walk through the external objects and add them to the [parts] section
    of the Configuration."""

    # import the Configuration class to use its functions
    from amira_blender_rendering.datastructures import Configuration

    for i, obj in enumerate(context.scene.abr_external_objects):
        config[obj.name] = Configuration()
        config[obj.name].name = obj.name
        config[obj.name].file_path = obj.file_path
        config[obj.name].scale = obj.scale


def build_target_objects_string(context):
    """Compute the 'target_objects' string for the Configuration.

    This string is of the format "parts.obj_name:count", where "parts" is
    omitted in case that the object is from within the blender file, and
    written out if the object is one of the external parts listed in the [parts]
    section of the configuration.
    """

    target_objects = []

    # walk through internal objects
    for obj in bpy.data.objects:
        # exclude cameras, objects which we're not aware of, and objects we don't
        # want to track.
        if not obj.type == 'MESH':
            continue
        if not hasattr(obj, 'abr_object_config'):
            continue
        if not obj.abr_object_config.track_object:
            continue
        if obj.abr_object_config.is_instantiated_object:
            continue
        target_objects.append(f'{obj.name}:{obj.abr_object_config.instance_count}')

    # walk through external objects
    for i, obj in enumerate(context.scene.abr_external_objects):
        target_objects.append(f'parts.{obj.name}:{obj.count}')

    # make a nice string of the result
    return ', '.join(target_objects)




# conversion functions to convert between Blender and Configuration
def config_to_blender(context, filepath, report_fn):
    """Take a configuration file and load it into blender.

    This will store all configurable parameters within the blender file, and
    further interaction with the configuration file is not required during
    editing from within blender.

    See also blender_to_config

    Args:
        context: Blender context
        filepath (str): Path to the configuration file
    """

    # TODO: clear everything within blender to avoid weird/wrong settings, then go through the config and convert every tiny little detail
    # TODO: how to handle camera_info

    # attempt to read the configuration
    from amira_blender_rendering.scenes import BaseConfiguration

    # we assume a base configuration, because this is the only thing we will expose
    # in the GUI. Using a base configuration will help us to get some types right
    config = BaseConfiguration()
    config.parse_file(filepath)

    # store the plain configuration to the scene for backup purposes.
    # NOTE: this is currently not used in the ABR plugin except for debug
    # purposes. We might think about updating the config string all the time
    # to easily export the configuration. However, this might have an impact on
    # UI latency, and it might be preferable to only compute the config string
    # during export
    context.scene.abr_plain_config_str = config.to_cfg()

    # update blender internal storage of configuration, that is also used
    # for updating the GUI
    context.scene.abr_dataset_config.from_config(config.dataset)
    context.scene.abr_scene_config.from_config(config.scene_setup)
    context.scene.abr_camera_config.from_config(config.camera_info)
    context.scene.abr_render_setup_config.from_config(config.render_setup)

    # process all targets and cameras in the configuration
    scan_targets(context, config, report_fn)
    scan_cameras(context, config, report_fn)


def build_camera_string(context):
    """Compute the 'cameras' string for the [scene_setup] section of the
    Configuration"""
    pass


def cameras_to_config(config, report_fn):
    """Write the camera_info for each camera that is used to the configuration.
    This function assumes that `config` is a `camera_info` section"""

    # import the Configuration class to use its functions
    from amira_blender_rendering.datastructures import Configuration

    cam_names = []
    for obj in bpy.data.objects:
        if not obj.type == 'CAMERA':
            continue
        else:
            if not hasattr(obj, 'abr_camera_config'):
                report_fn({'INFO'}, f"Camera {obj.name} lacks abr_camera_config. Not writing to config file.")
                continue
            # only write if this camera is used
            if obj.abr_camera_config.use_camera:
                cam_names.append(obj.name)
                if not obj.abr_camera_config.use_custom_configuration:
                    continue

                # create configuration
                config[obj.name] = Configuration()
                camera_cfg = config[obj.name]
                obj.abr_camera_config.to_config(camera_cfg)

    return cam_names


def blender_to_config(context, report_fn):
    """Turn the configuration that we keep in blender into a Configuration
    object."""

    # import the Configuration class to use its functions
    from amira_blender_rendering.datastructures import Configuration

    # instantiate a Configuration
    config = Configuration()

    # save all information from blender to the configuration

    # (global) dataset configuration
    config.dataset = Configuration()
    context.scene.abr_dataset_config.to_config(config.dataset)

    # scene setup
    config.scene_setup = Configuration()
    context.scene.abr_scene_config.to_config(config.scene_setup)


    # write all camera information
    config.camera_info = Configuration()
    context.scene.abr_camera_config.to_config(config.camera_info)
    # scan all cameras in the scene for detailed camera information, and add
    # this information also to the scene_setup
    camera_names = cameras_to_config(config.camera_info, report_fn)
    config.scene_setup.cameras = ', '.join(camera_names)

    # render setup
    config.render_setup = Configuration()
    context.scene.abr_render_setup_config.to_config(config.render_setup)

    # object information. First, all external objects
    config.parts = Configuration()
    external_objects_to_config(context, config.parts)

    # scenario setup
    config.scenario_setup = Configuration()
    config.scenario_setup.target_objects = build_target_objects_string(context)
    # NOTE: any additional scenario-setup, such as ABC Colors or Objects should
    # go here.

    return config


classes = (
    # All classes defined in this file that blender should be aware of
      StringValue
    , AmiraDatasetConfiguration
    , AmiraSceneConfiguration
    , AmiraObjectConfiguration
    , AmiraCameraIntrinsics
    , AmiraCameraZeroing
    , AmiraCameraConfiguration
    , AmiraExternalObject
    , AmiraRenderSetup
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # scene specific properties (we also store the dataset configuration here)
    bpy.types.Scene.abr_dataset_config      = bpy.props.PointerProperty(type=AmiraDatasetConfiguration)
    bpy.types.Scene.abr_scene_config        = bpy.props.PointerProperty(type=AmiraSceneConfiguration)
    bpy.types.Scene.abr_camera_config       = bpy.props.PointerProperty(type=AmiraCameraConfiguration)
    bpy.types.Scene.abr_render_setup_config = bpy.props.PointerProperty(type=AmiraRenderSetup)
    # we also attempt to store the plain configuration, in case the user changes it
    bpy.types.Scene.abr_plain_config_str = bpy.props.StringProperty( \
        name='Plain ABR Configuration',
        description='This string contains the plain, potentially modified, configuration for ABR',
        default='')
    # we might have a collection of external objects that should be imported in the dataset
    bpy.types.Scene.abr_external_objects = bpy.props.CollectionProperty(type=AmiraExternalObject)
    bpy.types.Scene.abr_external_objects_index = bpy.props.IntProperty()

    # object and camera configs
    bpy.types.Object.abr_object_config = bpy.props.PointerProperty(type=AmiraObjectConfiguration)
    bpy.types.Object.abr_camera_config = bpy.props.PointerProperty(type=AmiraCameraConfiguration)


def unregister():

    del bpy.types.Scene.abr_dataset_config
    del bpy.types.Scene.abr_scene_config
    del bpy.types.Scene.abr_camera_config
    del bpy.types.Scene.abr_render_setup_config
    del bpy.types.Scene.abr_plain_config_str
    del bpy.types.Scene.abr_external_objects
    del bpy.types.Scene.abr_external_objects_index

    del bpy.types.Object.abr_object_config
    del bpy.types.Object.abr_camera_config

    for cls in classes:
        bpy.utils.unregister_class(cls)
