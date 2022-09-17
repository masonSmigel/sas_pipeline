"""
This module creates a menu for a SAS pipeline
"""
import imp
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class RiggingMenu(subMenuBase.SubMenu):
    def __init__(self, name='rigging', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(RiggingMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the rigging subMenu"""
        # look for rigamajig in the users python path if it exists add rigamajig to the menu.
        try:
            imp.find_module('rigamajig2')
            found = True
        except ImportError:
            found = False

        if found:
            self.addMenuItem("Rigamajig2 Builder", command=openRigamajigBuilder)
            self.addDivider()
            self.addMenuItem("Reload Rigamajig2", command=reloadRigamajig)


# functions explicitly connected to rigamajig2
def openRigamajigBuilder(*args):
    """Open the rigamajig Builder"""
    import rigamajig2.ui.builder_ui.dialog as builder_dialog
    builder_dialog.BuilderDialog.showDialog()


def reloadRigamajig(*args):
    import rigamajig2
    rigamajig2.reloadModule()
