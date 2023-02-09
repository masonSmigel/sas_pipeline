"""
This module creates a menu for a SAS pipeline
"""
import imp
import os
import maya.cmds as cmds
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase

PLAYBLAST_PATH = "playblast"


class AnimationMenu(subMenuBase.SubMenu):
    def __init__(self, name='animation', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(AnimationMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            self.addMenuItem("Apply Mocap Data", command=applyMocapData)
            self.addMenuItem("Select Whole Character", command=selectWholeCharacter)
            self.addMenuItem("IkFk Match Selected", command=ikfkMatchSelectedComponent)
            self.addDivider()
            self.addMenuItem("Batch FBX Exporter", command=openBatchFBXExporter)
            self.addDivider()

        self.addMenuItem("Quick Playblast", command=quickPlayblast)

        # try to import tween machine
        try:
            imp.find_module('tweenMachine')
            found = True
        except ImportError:
            found = False

        if found:
            self.addDivider()
            self.addMenuItem("Tween Machine", command=openTweenMachine)


# functions explicitly connected to rigamajig2
def applyMocapData(*args):
    from rigamajig2.maya.anim import mocap
    mocap.MocapImportDialog.showDialog()


def selectWholeCharacter(*args):
    """Select a character from a single selected control """
    from rigamajig2.maya.rig import control
    from rigamajig2.maya import namespace
    import maya.cmds as cmds

    selection = cmds.ls(sl=True)

    if len(selection) > 0:
        controlNamespace = namespace.getNamespace(selection[0])
        controls = control.getControls(namespace=controlNamespace)
        cmds.select(controls)
    else:
        raise Exception("Please select a control on the character you wish to select")


def ikfkMatchSelectedComponent(*args):
    """ IkFk math the selected component"""
    from rigamajig2.maya.anim import ikfkSwitcher
    ikfkSwitcher.switchSelectedComponent()


def openTweenMachine(*args):
    """Open the tween machine"""
    import tweenMachine
    tweenMachine.start()


def openBatchFBXExporter(*args):
    """ Open the batch exporter"""
    from rigamajig2.maya.anim import ueExport
    ueExport.BatchExportFBX().showDialog()


def quickPlayblast(*args):
    """ perform a quick playblast and place the file in a playblast folder"""
    currentFile = cmds.file(q=True, sn=True)
    baseDirectory = os.path.dirname(currentFile)
    fileName = os.path.basename(currentFile).split(".")[0]

    playblastPath = os.path.abspath(os.path.join(baseDirectory, PLAYBLAST_PATH))

    # check if the path exisits. if not create it
    if not os.path.exists(playblastPath):
        os.makedirs(playblastPath)

    # build the full path
    fullPath = os.path.join(playblastPath, fileName)

    # get infor from your scene about the render
    startTime = cmds.playbackOptions(q=True, ast=True)
    endTime = cmds.playbackOptions(q=True, aet=True)

    w = cmds.getAttr("defaultResolution.width")
    h = cmds.getAttr("defaultResolution.height")

    # perform the playblast
    cmds.playblast(startTime=startTime,
                   endTime=endTime,
                   filename=fullPath,
                   percent=100,
                   showOrnaments=False,
                   format="movie",
                   compression="h.264",
                   wh=(w, h))
