#!/usr/bin/env python

import os
import bpy
from amira_blender_rendering import blender_utils as blnd
from amira_blender_rendering import utils

# XXX: i don't like these global variables, but taken from other files from
# within amira_blender_rendering. Essentially, this just works around having a
# singleton somehwere. But also singletons are not really a good idea...
logger = utils.get_logger()

class BaseSceneManager():
    """Class for arbitrary scenes that should be set up for rendering data.

    This class is inspired by tests.test_panda:SceneManager, and should act as an
    an entry point for arbitrary scenarios. Ideal
    """

    def __init__(self):
        super(BaseSceneManager, self).__init__()

    def reset(self):
        blnd.clear_all_objects()
        blnd.clear_orphaned_materials()

    def set_environment_texture(self, filepath):
        """Set a specific environment texture for the scene"""

        # check if path exists or not
        if not os.path.exists(filepath):
            logger.error(f"Path {filepath} to environment texture does not exist.")
            return

        # add new environment texture node if required
        tree = bpy.context.scene.world.node_tree
        nodes = tree.nodes
        if 'Environment Texture' not in nodes:
            nodes.new('ShaderNodeTexEnvironment')
        n_envtex = nodes['Environment Texture']

        # retrieve image object and set
        img = blnd.load_img(filepath)
        n_envtex.image = img

        # setup link (doesn't matter if already exists, won't duplicate)
        tree.links.new(n_envtex.outputs['Color'], nodes['Background'].inputs['Color'])


# TODO: this should become a UnitTest
if __name__ == "__main__":
    mgr = BaseSceneManager()
    mgr.set_environment_texture(os.path.expanduser('~/gfx/assets/hdri/machine_shop_02_4k.hdr'))