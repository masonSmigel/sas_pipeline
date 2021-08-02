import re

import pymel.core as pm
import maya.mel as mel


def _null(*args):
    pass


class _shelf:
    """
    A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".
    """

    def __init__(self, name="customShelf", iconPath=""):
        self.name = name
        self.shelf_obj = re.sub("[^A-Za-z0-9_{}]", "", str(self.name))

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        pm.setParent(self.shelf_obj)
        self.build()

    def build(self):
        """
        This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.
        """
        pass

    def addButon(self, label, icon="commandButton.png", command=_null, doubleCommand=_null):
        """Adds a shelf button with the specified label, command, double click command and image."""
        pm.setParent(self.shelf_obj)
        if icon:
            icon = self.iconPath + icon
        pm.shelfButton(width=37, height=37, image=icon, l=label, command=command, dcc=doubleCommand,
                       olb=self.labelBackground, olc=self.labelColour)

    def addMenuItem(self, parent, label, command=_null, icon=""):
        """
        Adds a shelf button with the specified label, command, double click command and image.
        """
        if icon:
            icon = self.iconPath + icon
        return pm.menuItem(p=parent, l=label, c=command, i="")

    def addSubMenu(self, parent, label, icon=None):
        """
        Adds a sub menu item with the specified label and icon to the specified parent popup menu.
        """
        if icon:
            icon = self.iconPath + icon
        return pm.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self):
        """
        Checks if the shelf exists and empties it if it does or creates it if it does not.
        """
        main_shelf = mel.eval('$tempMelVar=$gShelfTopLevel')

        if pm.shelfLayout(self.shelf_obj, ex=1):
            if pm.shelfLayout(self.shelf_obj, q=1, ca=1):
                for each in pm.shelfLayout(self.shelf_obj, q=1, ca=1):
                    pm.deleteUI(each)
        else:
            pm.shelfLayout(self.shelf_obj, p=main_shelf)

    def teardown(self):
        pm.deleteUI(self.shelf_obj)
