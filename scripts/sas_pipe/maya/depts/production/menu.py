"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
from sas_pipe.maya.widgets import subMenuBase


class ProductionMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=common.ICONS_PATH):
        super(ProductionMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        self.addMenuItem("Add Show")
        self.addMenuItem("Delete Show")
        self.addDivider()
        self.addMenuItem("Add Element")
        self.addMenuItem("Delete Element")
        self.addDivider()
        self.addMenuItem("Add Shot")
        self.addMenuItem("Delete Shot")

