"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class ModellingMenu(subMenuBase.SubMenu):
    def __init__(self, name='Modelling', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(ModellingMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            self.addMenuItem("Clean Model", command=cleanSelectedModel)
            self.addMenuItem("Clean ColorSets", command=cleanColorSet)


# functions explicitly connected to rigamajig2
def cleanSelectedModel(*args):
    """Clean the selected model"""
    from rigamajig2.maya import mesh
    import maya.cmds as cmds 
    sel = cmds.ls(sl=True)
    mesh.cleanModel(sel)


# functions explicitly connected to rigamajig2
def cleanColorSet(*args):
    """Clean the selected model"""
    from rigamajig2.maya import mesh
    import maya.cmds as cmds
    sel = cmds.ls(sl=True)
    mesh.cleanColorSets(sel)
