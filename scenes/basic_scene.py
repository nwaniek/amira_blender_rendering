#!/usr/bin/env python

# NOTE: You should ignore any properties that are set on blender objects via
#       our blender plugin! Rather, take all configuration from the
#       Configuration object that your scene gets in its constructor. The reason
#       for this behavior is that scene backend scripts are primarily intended
#       for generation of large datasets on a compute cluster. For this, you
#       might want to pass in several different configurations to `abrgen`. In
#       our case, we automatically generate and sometimes dynamically modify
#       these configurations. Hence, the *only valid truth* regarding
#       configurations and properties for any backend script should be the
#       configuration that it receives in `__init__`.


# Give some information about the scene backend script. At the moment, we don't
# explicitly use this information in ABR, but for documentation purposes.
backend_script_info = {
    "name":         "Basic Scene",
    "author":       "The AMIRA Team",
    "version":      (0, 1),
    "description":  "A simple example for a backend script"
}

# The two primary imports to get ABR's functionality
import amira_blender_rendering as abr
import amira_blender_rendering.interfaces as abr_interfaces

#
# Each scene should be derived from ABRScene, or a subclass thereof. The reason
# is that our blender plugin will look for subclasses of ABRScene when
# generating and automatically updating the GUI.
#
# When deriving from ABRScene, you need to implement a basic set of methods that
# are required for dataset generation. Anything beyond this set of methods is
# custom code that you can (and should) adapt to your needs. However, we provide
# several convenience functions and classes that should help to quickly set up
# scene backend scripts. For instance, there's RenderManager and
# BaseSceneManager, which help you set up scenes and the rendering environment.
#
# For more information on how to use these classes and how to derive from
# BasicScene, please see the example below.
#
#
class BasicScene(abr_interfaces.ABRScene):

    def __init__(self, **kwargs):
        super(BasicScene, self).__init__()

        # extract configuration
        self.config = kwargs.get('config', None)

        # figure out if we're running in interactive mode - that is, from within
        # blender or not
        self.interactive = kwargs.get('interactive', False)

    def generate_one(self):
        print("Generate One from within BasicScene")
        pass

    def generate_dataset(self):
        pass

    def teardown(self):
        pass


# generation.
class BasicScene2(abr_interfaces.ABRScene):

    def __init__(self, **kwargs):
        super(BasicScene2, self).__init__()

        # extract configuration
        self.config = kwargs.get('config', None)

        # figure out if we're running in interactive mode - that is, from within
        # blender
        self.interactive = kwargs.get('interactive', False)

    def generate_one(self):
        print("Generate One from within BasicScene2")
        pass

    def generate_dataset(self):
        pass

    def teardown(self):
        pass

