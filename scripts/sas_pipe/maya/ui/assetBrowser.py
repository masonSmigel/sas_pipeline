"""
This module contains the asset browser UI
"""
import sys
import os

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


class AssetBrowser(QtWidgets.QDialog):
    WINDOW_TITLE = "SAS Asset Browser"

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SASAssetBrowser()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self):
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        else:
            maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

        super(AssetBrowser, self).__init__(maya_main_window)
        self.rig_env = None

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setProperty("saveWindowPref", True)
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(825, 625)

        self.create_actions()
        self.create_menus()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        pass

    def create_menus(self):
        pass

    def create_widgets(self):
        self.studio_path_le = QtWidgets.QLineEdit()
        self.studio_path_le.setPlaceholderText("studio/...")

        self.set_studio_btn = QtWidgets.QPushButton("...")
        self.set_studio_btn.setFixedWidth(30)

        self.show_comboBox = QtWidgets.QComboBox()
        self.show_comboBox.setFixedWidth(120)

        self.browser1 = QtWidgets.QTreeWidget()
        self.browser2 = QtWidgets.QTreeWidget()

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.show_grp = QtWidgets.QGroupBox('Show')
        self.show_grp.setFixedHeight(70)
        show_layout = QtWidgets.QHBoxLayout()

        show_layout.addWidget(QtWidgets.QLabel("Studio: "))
        show_layout.addWidget(self.studio_path_le)
        show_layout.addWidget(self.set_studio_btn)
        show_layout.addSpacing(50)
        show_layout.addWidget(QtWidgets.QLabel("Show: "))
        show_layout.addWidget(self.show_comboBox)

        self.entities_grp = QtWidgets.QGroupBox('File Browser')
        entities_layout = QtWidgets.QHBoxLayout()

        self.show_grp.setLayout(show_layout)
        self.entities_grp.setLayout(entities_layout)

        entity_splitter = QtWidgets.QSplitter()
        entity_splitter.setOrientation(QtCore.Qt.Horizontal)
        entities_layout.addWidget(entity_splitter)

        entity_splitter.addWidget(self.browser1)
        entity_splitter.addWidget(self.browser2)

        # add groups to main layout
        main_layout.addWidget(self.show_grp)
        main_layout.addWidget(self.entities_grp)

    def create_connections(self):
        pass


if __name__ == '__main__':
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = SASAssetBrowser()
    dialog.show()
