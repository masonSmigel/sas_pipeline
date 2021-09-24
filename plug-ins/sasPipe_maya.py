"""Plugin for maya SAS Pipeline"""

import inspect
import os
import sys
import traceback

import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds
import pymel.util

python_root = None
UI_CREATED = list()


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class SASPipe(OpenMaya.MPxCommand):
    kPluginCmdName = "sasPipe"

    @staticmethod
    def cmdCreator():
        return SASPipe()

    def __init__(self):
        super(SASPipe, self).__init__()

    def doIt(self, argList):
        raise Exception('Plugin not supposed to be invoked - only loaded or unloaded.')


def initializePlugin(obj):
    """
    :param obj: OpenMaya.MObject
    """
    plugin = OpenMaya.MFnPlugin(obj, 'SCAD Animation Studios', '1.0.1', 'Any')
    try:
        plugin.registerCommand(SASPipe.kPluginCmdName, SASPipe.cmdCreator)
        load()

    except Exception as e:
        raise RuntimeError('Failed to register command: {}\nDetails:\n{}'.format(e, traceback.format_exc()))


def uninitializePlugin(obj):
    """
    :param obj: OpenMaya.MObject
    """
    plugin = OpenMaya.MFnPlugin(obj)
    try:
        teardown()
        plugin.deregisterCommand(SASPipe.kPluginCmdName)
    except Exception as e:
        raise RuntimeError('Failed to unregister command: {}\nDetails:\n{}'.format(e, traceback.format_exc()))


def load():
    """
    On initialization, this function gets called to:
    - Add plug in paths to the Maya environment
    - Add Python root path to sys.path
    - Create a mod file in user local that adds plug in path to this plug in to retain auto load
    - Setup the SAS Pipeline menu
    """
    plugPath = inspect.getfile(inspect.currentframe())
    plugin_folder_path = os.path.abspath(os.path.join(plugPath, os.pardir)).replace('\\', '/')

    python_root = os.path.join(os.path.dirname(plugin_folder_path), 'scripts')

    if python_root not in sys.path:
        sys.path.append(python_root)

    # Setup the tools
    import sas_pipe.maya.sas_menu as sas_menu
    import sas_pipe.maya.maya_pipe as maya_pipe
    from sas_pipe.shared.logger import Logger

    _sas_menu = sas_menu.SASMenu(name='SAS Pipeline')
    UI_CREATED.append(_sas_menu.menu_obj)
    if not maya_pipe.MayaPipeline.validate_root():
        import sas_pipe.maya.ui.set_root as set_root
        set_root.run()
    pipe = maya_pipe.MayaPipeline()
    if pipe.current_show is None:
        Logger.warning('No show is set!')


def teardown():
    """
    On uninitialization, this function gets called to:
    - Remove Python root path from sys.path
    - Delete any UIs we have created
    """

    # Remove our Python root from sys.path
    for sysPath in sys.path:
        if sysPath == python_root:
            sys.path.remove(sysPath)

    # Delete our UI
    for ui in UI_CREATED:
        cmds.deleteUI(ui)
