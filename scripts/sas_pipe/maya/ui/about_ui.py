import os

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe
import sas_pipe.shared.common as common


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AboutUi(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = AboutUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(AboutUi, self).__init__(parent)

        self.setWindowTitle("About")  # Window title name
        self.setFixedSize(200, 300)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "about.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        pixmap = QtGui.QPixmap(os.path.join(common.ICONS_PATH, 'sas_x64.png'))
        self.ui.logo_label.setGeometry(50, 40, 250, 250)
        self.ui.logo_label.setPixmap(pixmap)

        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.close_btn.clicked.connect(self.close)

    def on_show(self):
        self.ui.vendor_label.setText(cmds.pluginInfo('sasPipe_maya.py', q=True, vendor=True))
        self.ui.plugin_label.setText(cmds.pluginInfo('sasPipe_maya.py', q=True, version=True))
        self.ui.framework_label.setText(sas_pipe.__version__)
