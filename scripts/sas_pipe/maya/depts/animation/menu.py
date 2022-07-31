"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
from sas_pipe.maya.widgets import subMenuBase


class AnimationMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=common.ICONS_PATH):
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


# functions explicitly connected to rigamajig2
def applyMocapData(*args):
    from rigamajig2.maya.anim import mocap
    mocap.MocapImportDialog.showDialog()