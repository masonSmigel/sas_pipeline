"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class AnimationMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
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
            self.addMenuItem("Select Whole Character", command=applyMocapData)


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