"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class RiggingMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(RiggingMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            self.addMenuItem("Rigamajig2 Builder", command=openRigamajigBuilder)
            self.addDivider()
            self.addMenuItem("Select Controls", command=selectControls)
            self.addMenuItem("Select Bind Joints", command=selectBindJoints)

            self.addMenuItem("Create Axis Marker", command=createAxisMarker)
            self.addDivider()
            self.addMenuItem("Copy Weights and Influences", command=copyWeightsAndInfluences)
            self.addDivider()
            self.addMenuItem("Reload Rigamajig2", command=reloadRigamajig)


# functions explicitly connected to rigamajig2
def openRigamajigBuilder(*args):
    """Open the rigamajig Builder"""
    import rigamajig2.ui.builder_ui.dialog as builder_dialog
    builder_dialog.BuilderDialog.showDialog()


def reloadRigamajig(*args):
    import rigamajig2
    rigamajig2.reloadModule()


def selectControls(*args):
    import rigamajig2.maya.rig.control as ctl
    cmds.select(ctl.getControls())


def selectBindJoints(*args):
    import rigamajig2.maya.meta
    import maya.cmds as cmds

    cmds.select(rigamajig2.maya.meta.getTagged("bind"))


def createAxisMarker(*args):
    import rigamajig2.maya.debug as debug
    debug.createAxisMarker()


def copyWeightsAndInfluences(*args):
    import maya.cmds as cmds
    import rigamajig2.maya.skinCluster as rig_skinCluster

    src = cmds.ls(sl=True)[0]
    dst = cmds.ls(sl=True)[1:]

    rig_skinCluster.copySkinClusterAndInfluences(src, dst)