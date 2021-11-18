import os

import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import __trash__.maya.maya_pipe as maya_manager


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class SetShowUI(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SetShowUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(SetShowUI, self).__init__(parent)

        self.setWindowTitle("Set Show")  # Window title name
        self.setObjectName('SetShowDialog')  # Window object name
        self.setFixedSize(240, 90)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "set_show.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.pipe = maya_manager.MayaPipeline()
        shows = self.pipe.get_shows(base_only=True)
        for show in shows:
            self.ui.shows_cbox.addItem(show)

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)

    def ok(self):
        selected_show = self.ui.shows_cbox.currentText()
        self.pipe.set_show(selected_show)
        self.close()
