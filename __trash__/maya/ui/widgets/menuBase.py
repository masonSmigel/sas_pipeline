import re

import pymel.core as pm


def _null(*args):
    pass


class _menu:
    """
    A simple class to build menus in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf".
    """

    def __init__(self, name="customMenu", iconPath=""):
        self.name = name
        self.menu_obj = re.sub("[^A-Za-z0-9_{}]", "", str(self.name) + 'Menu')

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldMenu()
        # pm.setParent(self.name)
        self.build()

    def build(self):
        """
        This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf.
        """
        pass

    def addMenuItem(self, label, parent=None, command=_null, icon="", **kwargs):
        """
        Adds a shelf button with the specified label, command, double click command and image.
        """
        if icon:
            icon = self.iconPath + icon
        if not parent:
            parent = self.menu_obj
        return pm.menuItem(p=parent, l=label, c=command, i=icon, **kwargs)

    def addSubMenu(self, label, parent=None, icon=None, tearOff=True, **kwargs):
        """
        Adds a sub menu item with the specified label and icon to the specified parent popup menu.
        """
        if icon:
            icon = self.iconPath + icon
        if not parent:
            parent = self.menu_obj
        return pm.menuItem(l=label, subMenu=True, tearOff=tearOff, p=parent, **kwargs)

    def addDivider(self, parent=None):
        """
        Add a separator
        """
        if not parent:
            parent = self.menu_obj
        return pm.menuItem(divider=True, parent=parent)

    def _cleanOldMenu(self):
        """
        Checks if the shelf exists and empties it if it does or creates it if it does not.
        """
        main_window = pm.language.melGlobals['gMainWindow']

        if pm.menu(self.menu_obj, l=self.name, ex=1):
            if pm.menu(self.menu_obj, q=True, ia=True):
                for each in pm.menu(self.menu_obj, q=True, ia=True):
                    pm.deleteUI(each)

        else:
            pm.menu(self.menu_obj, l=self.name, p=main_window, tearOff=True)

    def teardown(self):
        pm.deleteUI(self.menu_obj)
