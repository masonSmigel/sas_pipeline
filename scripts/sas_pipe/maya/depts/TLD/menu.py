"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class TLDMenu(subMenuBase.SubMenu):
    def __init__(self, name='TLD', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(TLDMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            self.addMenuItem("Shatter Selected Skeleton", command=openShatterSkeleton)


# functions explicitly connected to rigamajig2
def openShatterSkeleton(*args):
    """Open the rigamajig Builder"""
    from sas_pipe.maya.depts.TLD import shatterSkeleton
    from rigamajig2.maya import namespace
    import maya.cmds as cmds

    selection = cmds.ls(sl=True)

    if len(selection) > 0:
        controlNamespace = namespace.getNamespace(selection[0])

    shatterSkeleton.run(namespace=controlNamespace)

