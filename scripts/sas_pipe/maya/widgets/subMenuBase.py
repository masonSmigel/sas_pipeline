import re


import maya.cmds as cmds
import maya.mel as mel

from sas_pipe import path

def _null(*args):
    pass


class SubMenu(object):
    """
    A simple class to build menus in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".
    """

    def __init__(self, name="customMenu", parent=None, iconPath=""):
        self.name = name

        self.parent=parent
        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self.build()

    def build(self):
        """
        This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.
        """
        pass

    def addMenuItem(self, label, parent=None, command=_null, icon=str(), **kwargs):
        """
        Adds a shelf button with the specified label, command, double click command and image.
        """
        if icon:
            iconpath = self.iconPath + icon
            icon = iconpath if path.is_file(iconpath) else ''

        if not parent:
            parent = self.parent
        return cmds.menuItem(p=parent, l=label, c=command, i=icon, **kwargs)

    def addSubMenu(self, label, parent=None, icon=None, tearOff=True, **kwargs):
        """
        Adds a sub menu item with the specified label and icon to the specified parent popup menu.
        """
        if not parent:
            parent = self.parent
        return cmds.menuItem(l=label, subMenu=True, tearOff=tearOff, p=parent, **kwargs)

    def addDivider(self, parent=None):
        """
        Add a separator
        """
        if not parent:
            parent = self.parent
        return cmds.menuItem(divider=True, parent=parent)
