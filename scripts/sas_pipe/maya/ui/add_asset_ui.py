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


class AddAssetUI(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = AddAssetUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(AddAssetUI, self).__init__(parent)

        self.setWindowTitle("Add Asset")  # Window title name
        self.setFixedSize(270, 150)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "add_asset.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.update_all_ui()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.assetType_cb.currentIndexChanged.connect(self.update_path_display)
        self.ui.assetName_le.textChanged.connect(self.update_path_display)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.apply_btn.clicked.connect(self.apply)

    def apply(self):
        asset_name = self.ui.assetName_le.text()
        if asset_name:
            clean_name = re.sub("[^A-Za-z0-9_{}.]", "", str(asset_name))
            asset_task = self.ui.assetType_cb.currentText()
            self.pipe.add_asset(clean_name, asset_task)
            self.ui.assetName_le.clear()
        else:
            Logger.warning('You must supply an asset name')

    def ok(self):
        self.apply()
        self.close()

    def update_all_ui(self):
        self.pipe = maya_manager.MayaManager()
        tasks = self.pipe.settings['asset_types']
        self.ui.assetType_cb.clear()
        for task in tasks:
            self.ui.assetType_cb.addItem(task)
        self.update_path_display()

    def update_path_display(self):
        path = os.path.join(self.pipe.asset_work_path, self.ui.assetType_cb.currentText(), self.ui.assetName_le.text())
        self.ui.path_le.setText(self.pipe.get_relative_path(path))

    def on_show(self):
        new_pipe = maya_manager.MayaManager()
        if not new_pipe.current_show == self.pipe.current_show:
            self.pipe = new_pipe
            self.update_all_ui()
