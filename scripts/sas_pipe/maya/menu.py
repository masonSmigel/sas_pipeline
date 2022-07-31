"""
This module creates a menu for a SAS pipeline
"""
import imp
import os
import inspect
import sas_pipe.common as common
import sas_pipe.maya.widgets.menuBase as menuBase

DEPTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'depts'))

EXCLUDED_FOLDERS = list()
EXCLUDED_FILES = ['__init__.py']


def _findMenus(path, excludedFolders, excludedFiles):
    """
    Find  menus within the departments.

    A menu added if:
     there is a menu.py file within the department folder
     the menu.py file has a class with the name of the department with "Menu" appended.
        ex. "RiggingMenu"


    :param path:
    :param excludedFolders:
    :param excludedFiles:
    :return:
    """
    res = os.listdir(path)
    toReturn = list()
    for r in res:
        fullList = os.path.join(path, r)
        if r not in excludedFolders and os.path.isdir(path + '/' + r):
            found = _findMenus(fullList, excludedFolders, excludedFiles)
            if len(found) > 0:
                toReturn += found
        if r.find('.py') != -1 and r.find('.pyc') == -1 and r not in excludedFiles:
            if r.find('reload') == -1:
                if r == "menu.py":
                    moduleFile = r.split('.')[0]
                    pathSplit = fullList.split('/')[:-1]

                    localPath = '.'.join(pathSplit[pathSplit.index("depts"):])
                    componentName = '{}.{}'.format(localPath, moduleFile)
                    fullModuleName = "sas_pipe.maya.{}".format(componentName)

                    moduleObject = __import__(fullModuleName, globals(), locals(), ["*"], 0)
                    className = pathSplit[-1].capitalize() + "Menu"

                    for cls in inspect.getmembers(moduleObject, inspect.isclass):
                        # if the class matches the predicted name append the class object to the toReturn list.
                        if cls[0] == className:
                            toReturn.append(cls)
    return toReturn


class MainMenu(menuBase._menu):
    def __init__(self, name='SAS_pipeline', iconsPath=common.ICONS_PATH):
        super(MainMenu, self).__init__(name=name, iconPath=iconsPath)

    def build(self):
        set_menu = self.addSubMenu("Setup Project")
        self.addMenuItem("Set Studio", parent=set_menu)
        self.addMenuItem("Set Show", parent=set_menu)

        self.addDivider()

        self.addMenuItem("Browse Entities", command=open_asset_browser)
        self.addMenuItem("Publish File", command=open_publish_file)

        self.addDivider()

        # for each department look for a menu.py file if one exists then we can

        for subMenuData in _findMenus(DEPTS_PATH, EXCLUDED_FOLDERS, EXCLUDED_FILES):
            subMenuName = subMenuData[0].replace("Menu", "")
            submenu = subMenuData[-1]
            subMenuName = subMenuName
            riggingMenu = self.addSubMenu(subMenuName)
            submenu(parent=riggingMenu)


        self.addDivider()
        help_menu = self.addSubMenu("Help")
        self.addMenuItem("Documentation", parent=help_menu, command=open_documentation)
        self.addMenuItem("About", parent=help_menu)


def open_asset_browser(*args):
    import sas_pipe.maya.ui.assetBrowser as assetBrowser
    assetBrowser.SAS_AssetBrowser().show_dialog()


def open_publish_file(*args):
    import sas_pipe.maya.ui.publishFile as publishFile
    publishFile.PublishEntityUi().show_dialog()


def open_documentation(*args):
    import urllib
    return urllib.urlopen('https://github.com/masonSmigel/sas_pipeline/tree/v2.0.0')


def show_about():
    pass


# functions explicitly connected to rigamajig2
def applyMocapData(*args):
    import rigamajig2.maya.anim.mocap as mocap
    mocap.MocapImportDialog.show_dialog()
