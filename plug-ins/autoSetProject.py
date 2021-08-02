"""
Plugin to automatically set the maya project when a file opens.

Derived from mSetProject which is not supported in versions after maya 2020
original author website: www.skymill.co.jp

Author: Mason Smigel
Date: July 2021
Version: 01.00
"""

import inspect
import sys
import os
import traceback

import maya.api.OpenMaya as om2
import maya.OpenMaya as om
import pymel.core as pm
import pymel.util

callbackId = None


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class AutoSetProject(om2.MPxCommand):
    kPluginCmdName = "autoSetProj"

    @staticmethod
    def cmdCreator():
        return AutoSetProject()

    def __init__(self):
        super(AutoSetProject, self).__init__()

    def doIt(self, argList):
        raise Exception('Plugin not supposed to be invoked - only loaded or unloaded.')


def initializePlugin(obj):
    """
    :param obj: om2.MObject
    :return: None
    """
    plugin = om2.MFnPlugin(obj, 'Mason Smigel', '1.0.0', 'Any')
    try:
        plugin.registerCommand(AutoSetProject.kPluginCmdName, AutoSetProject.cmdCreator)
        load()

    except Exception as e:
        raise RuntimeError('Failed to register command: {}\nDetails:\n{}'.format(e, traceback.format_exc()))


def uninitializePlugin(obj):
    """
    :param obj: om2.MObject
    :return: None
    """
    plugin = om2.MFnPlugin(obj)
    try:
        teardown()
        plugin.deregisterCommand(AutoSetProject.kPluginCmdName)
    except Exception as e:
        raise RuntimeError('Failed to unregister command: {}\nDetails:\n{}'.format(e, traceback.format_exc()))


def load():
    """
    Setup the auto set project callback
    :return: None
    """
    # setup the callback
    global callbackId
    callbackId = om.MSceneMessage.addCheckFileCallback(om.MSceneMessage.kBeforeOpenCheck, set_project)
    print("callback {} created".format(str(callbackId)))


def teardown():
    """
    Remove the auto set project callback
    """
    global callbackId
    try:
        om.MMessage.removeCallback(callbackId)
    except:
        print('failed to remove callback {}'.format(str(callbackId)))


# Helper functions
def find_workspace(scene_path, limit=10):
    """
    look for a workspace.mel file in folder heirarchy
    :param scene_path: maya scene to search from
    :param limit: maximum number of folders above scene to look for.
    :returns: path to workspace.mel
    """
    path = scene_path[0: scene_path.rfind(os.path.basename(scene_path))]
    for i in range(limit):
        path = path[0:path.rfind(os.path.basename(path)) - 1]
        if path[-1:] != ":" and os.path.exists(path + "/workspace.mel"):
            return path


def set_project(retCode, fileObject, clientData=None):
    """
    Set maya project
    :param retCode: boolean passed in to the callback function. Incase of any error, this will be set to false in the callback function.
    :param fileObject: MFileObject maya file object to be acted on
    :param clientData: User defined data passed to the callback function
    """
    path = fileObject.rawFullName()

    current_workspace = pm.workspace.getPath()
    new_workspace = find_workspace(path)
    if new_workspace is not None and current_workspace is not new_workspace:
        pm.mel.setProject(new_workspace)

        # show the user the path has been changed
        om2.MGlobal.displayInfo("ms_setProject set project to: {}".format(new_workspace))
        display_path_msg(new_workspace)

    om.MScriptUtil.setBool(retCode, True)


def display_path_msg(msg):
    """
    show an inview message to alert the user the project was changed
    :param msg: string- path to display
    """
    Maya_version = pm.versions.current() / 100

    if Maya_version >= 2014:
        pm.inViewMessage(msg="Project set to: {}".format(msg), fade=True, fadeOutTime=2.0)
