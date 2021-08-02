import os
import re

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe.maya.maya_manager as maya_manager
import sas_pipe.shared.naming as naming
from sas_pipe.shared.logger import Logger


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class SaveVersionUi(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SaveVersionUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(SaveVersionUi, self).__init__(parent)

        self.setWindowTitle("Save Version")  # Window title name
        self.setFixedSize(320, 235)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        self.pipe = maya_manager.MayaManager()

        self.e = self.pipe.get_entity_from_curent_file()
        self.t = self.pipe.get_task_from_current_file()

        if self.e:
            f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "save_version.ui")))
            f.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            self.ui = loader.load(f, parentWidget=self)
            f.close()

            self.__update_feilds()
        else:
            f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "set_save_version.ui")))
            f.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            self.ui = loader.load(f, parentWidget=self)
            f.close()

            self.ui.fileBrowse_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
            self.ui.fileBrowse_btn.clicked.connect(self.file_browse)

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)

    def ok(self):
        warble = None
        if self.ui.warble_le:
            warble = re.sub("[^A-Za-z0-9_{}.]", "", str(self.ui.warble_le.text()))
        self.pipe.save_new_version(entity=self.e, task=self.t, file_type=self.pipe.settings['maya_file_type'],
                                   warble=warble)
        self.close()

    def file_browse(self):
        file_path = cmds.fileDialog2(ds=2, cap='Select a task in an asset or shot', dir=self.pipe.work_path, fm=2,
                                     okc='Open')
        if file_path:
            self.ui.path_le.setText(file_path[0])

            self.e = self.pipe.get_entity_from_curent_file(path=file_path[0])
            self.t = self.pipe.get_task_from_current_file(path=file_path[0])

            self.__update_feilds()

    def __update_feilds(self):
        if self.e:
            self.ui.path_le.setText(self.pipe.get_relative_path(self.e.path))
            self.ui.entity_le.setText(self.e.name)
            self.ui.task_le.setText(self.t)
            self.ui.versionIndex_le.setText(str(naming.get_highest_index(os.path.join(self.e.path, self.t)) + 1))
        else:
            Logger.warning('Invalid Task selected. Please Select a task within the Entity you are working on')
            self.ui.path_le.clear()
            self.ui.entity_le.clear()
            self.ui.task_le.clear()
            self.ui.versionIndex_le.clear()
