"""
This module creates a menu for a SAS pipeline
"""
import sas_pipe.common as common
import sas_pipe.maya.widgets.menuBase as menuBase


class SAS_menu(menuBase._menu):
    def __init__(self, name='SAS_pipeline', iconsPath=common.ICONS_PATH):
        super(SAS_menu, self).__init__(name=name, iconPath=iconsPath)

    def build(self):
        set_menu = self.addSubMenu("Set Enviornment")
        self.addMenuItem("Set Studio", parent=set_menu)
        self.addMenuItem("Set Show", parent=set_menu)

        self.addDivider()
        self.addMenuItem("Browse Entities")
        manage_menu = self.addSubMenu("Manage")
        self.addMenuItem("Add Show", parent=manage_menu)
        self.addMenuItem("Delete Show", parent=manage_menu)
        self.addDivider(parent=manage_menu)
        self.addMenuItem("Add Elm", parent=manage_menu)
        self.addMenuItem("Delete Elm", parent=manage_menu)
        self.addDivider(parent=manage_menu)
        self.addMenuItem("Add Shot", parent=manage_menu)
        self.addMenuItem("Delete Shot", parent=manage_menu)

        self.addDivider()
        tools_menu = self.addSubMenu("Tools")
        self.addMenuItem("Layout Master", parent=tools_menu)

        self.addDivider()
        self.addMenuItem("Command line")

        self.addDivider()
        help_menu = self.addSubMenu("Help")
        self.addMenuItem("Documentation", parent=help_menu)
        self.addMenuItem("About", parent=help_menu)
