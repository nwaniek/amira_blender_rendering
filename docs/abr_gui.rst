AMIRA Blender Rendering GUI Add-On
==================================

`abr_gui` is a blender GUI plugin which maps AMIRA Blender Rendering
configurations and operators into the blender UI. Specifically, all configurable
options from an ABR config file will be mapped to blender, most of which will
also be exposed within the GUI. That is, you will be able to edit the
configuration from within blender.

The purpose of this add-on is to allow visual debugging within blender. Without
the add-on, a usual scene debugging session goes by first rendering a few items
of a dataset with `abrgen`, opening the resulting images and data files, and
inspecting if the results are as expected. Sometimes, the generated data is
erroneous. For instance, numerical issues during physics simulations can lead to
objects that are not within view of any of the cameras. In such a case, a user
of `abrgen` has to open the original file and try to reproduce what caused the
problem. An easier solution is to set up a scene, and perform some data
generation for debugging purposes directly within blender. This is precisely
what this add-on is about.


Installation
------------

You can either install `abr_gui` from the `abr_gui.zip` file directly within
blender, or by copying or symlinking the `abr_gui` folder as described in the
section Development below. In any case, you must have the repository for
`amira_blender_rendering` checked out for full functionality.

After installation the Add-On in blender, make sure to go to the Add-On's
preferences within blender and set the path to ABR itself. That is, if
`~/dev/amira_blender_rendering` is the path to the checked out repository, the
path to ABR that you should specify is `~/dev/amira_blender_rendering/src`, as
this is the directory within which the core implementation of ABR resides.


Development
-----------

In case you wish to contribute to the development of this add-on, then one of
the easiest ways is as follows:

0. Check out the git repository of `amira_blender_rendering`. We assume that you
   have the repository at `~/dev/amira_blender_rendering` below.
1. Remove any installation of the `abr_gui` addon from blender, in case you
   previously installed it. You can do this in blender under Edit -> Preferences
   -> Addons. There, look for "Interfaces: AMIRA Blender Rendering GUI Add-On",
   and click the button "Remove". Close blender.
2. Go to the directory `~/.config/blender/X.YZ/scripts/addons`, where `X.YZ` is
   the version number of your blender installation, e.g. `2.91`. Within this
   directory, create a symlink to the `abr_gui` directory within the ABR
   repository, e.g. `ln -s ~/dev/amira_blender_rendering/src/amira_blender_addons/abr_gui`.
3. Start blender, go to the Preferences and enable the ABR GUI Addon.

During development, you might make changes to ABR or the `abr_gui` addon. If you
want to reload all plugins within blender such that changes you introcudes are
reflected, you can either hit F8 in blender, or hit the space bar, and select
"Reload Scripts".


