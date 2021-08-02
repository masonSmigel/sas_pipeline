""" Drag and Drop installer for Maya"""

import os
import sys

import pymel.util
import maya.cmds as cmds
import maya.mel as mel


def onMayaDroppedPythonFile(*args):
    installer_path = __file__

    module_root = os.path.dirname(installer_path)
    python_path = os.path.join(os.path.dirname(installer_path), 'scripts')
    icons_path  = os.path.join(os.path.dirname(installer_path),  'icons')
    plugin_path = os.path.join(os.path.dirname(installer_path),  'plug-ins')

    # Check if the modules directory exists in the user preference directory (if it doesn't, create it)
    maya_moddir_path = '{}/modules'.format(pymel.util.getEnv('MAYA_APP_DIR'))
    if not os.path.exists(maya_moddir_path):
        os.makedirs(maya_moddir_path)

    # Define the module file path
    maya_mod_file = '{}/sas_pipeline.mod'.format(maya_moddir_path)

    # Write our module file
    with open(maya_mod_file, 'w') as moduleFile:

        output = '+ sasPipe 1.0 {}'.format(module_root)

        # Add the path to plugin path on first use
        if plugin_path not in pymel.util.getEnv("MAYA_PLUG_IN_PATH"):
            pymel.util.putEnv("MAYA_PLUG_IN_PATH", [pymel.util.getEnv("MAYA_PLUG_IN_PATH"), plugin_path])

        # Any shelf file in this directory will be automatically loaded on Maya startup
        moduleFile.write(output)

    # add the python path on initalize
    if python_path not in sys.path:
        sys.path.append(python_path)

    # # Recursivly add all plugins within the python directory
    # for directory, subDirectories, filenames in os.walk(plugin_path):
    #     if os.path.basename(directory) != 'plugin':
    #         continue
    #     if len([filename for filename in filenames if
    #             '__init__' not in filename and filename.lower().endswith('.py')]) == 0:
    #         continue
    #
    #     plugin_folder_path = directory.replace('\\', '/')
    #
    #     # Add the plug in path so we can load it
    #     if plugin_folder_path not in pymel.util.getEnv("MAYA_PLUG_IN_PATH"):
    #         pymel.util.putEnv("MAYA_PLUG_IN_PATH", [pymel.util.getEnv("MAYA_PLUG_IN_PATH"), plugin_folder_path])
    #
    #     # attempt to load all plugins, .mod files are created in each plugin
    #     if [filename.endswith('.py') for filename in filenames]:
    #         print("loading {}".format(filename))
    #         cmds.loadPlugin(filename)
