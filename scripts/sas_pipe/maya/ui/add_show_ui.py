import os
import re

import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe.maya.maya_manager as maya_manager
from sas_pipe.shared.logger import Logger


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AddShowUI(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = AddShowUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(AddShowUI, self).__init__(parent)

        self.setWindowTitle("Add Show")  # Window title name
        self.setFixedSize(270, 85)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "add_show.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.apply_btn.clicked.connect(self.apply)

    def apply(self):
        show_name = self.ui.showName_le.text()
        if show_name:
            pipe = maya_manager.MayaManager()
            formatedName = show_name.upper()
            formatedName = re.sub("[^A-Z0-9]", "", str(formatedName))
            pipe.add_show(formatedName)
            pipe.set_show(formatedName)
            self.close()
        else:
            Logger.warning('You must supply a show name')

    def ok(self):
        self.apply()
        self.close()
