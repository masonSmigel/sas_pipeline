"""
This module creates a menu for a SAS pipeline
"""
import imp
from functools import partial

import maya.api.OpenMaya as om

import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class CommonMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(CommonMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            createNodeMenu = self.addSubMenu("Create Node")
            self.addMenuItem("Joint", parent=createNodeMenu, icon="/joint.png", command=partial(snapLocator, "joint"))
            self.addMenuItem("Locator", parent=createNodeMenu, icon="/locator.png",
                             command=partial(snapLocator, "locator"))
            self.addMenuItem("Transform", parent=createNodeMenu, icon="/transform.png",
                             command=partial(snapLocator, "null"))

            self.addMenuItem("Container Sanity Check", icon='/container.png', command=containerSanityCheck)


# functions explicitly connected to rigamajig2
def snapLocator(type, *args):
    import rigamajig2.sandbox.snapLoc as snapLoc
    snapLoc.createAtSelection(type=type)


def containerSanityCheck(*args):
    """ run the sainity check"""
    from rigamajig2.maya import container
    container.sainityCheck()
    om.MGlobal.displayInfo("Successfully ran sanity check container sanity check. ")
