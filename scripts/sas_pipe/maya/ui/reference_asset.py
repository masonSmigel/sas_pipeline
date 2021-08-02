import os

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe.maya.maya_manager as maya_manager
from sas_pipe.shared.logger import Logger


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ReferenceAssetUi(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = ReferenceAssetUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(ReferenceAssetUi, self).__init__(parent)

        self.setWindowTitle("Reference Asset")  # Window title name
        self.setFixedSize(310, 220)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "open_asset.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.ui.ok_btn.setText('Reference')
        self.ui.versions_label.setText('Publishes:')

        self.update_all_ui()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.assetType_cb.currentIndexChanged.connect(self.update_assets)
        self.ui.asset_cb.currentIndexChanged.connect(self.update_tasks)
        self.ui.task_cb.currentIndexChanged.connect(self.update_path_display)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.browse_btn.clicked.connect(self.browse)

    def ok(self):
        task = self.ui.task_cb.currentText()
        self.__get_asset_entity_obj()
        file = self.entity.get_publish(task=task, file_type=self.pipe.settings['maya_file_type'])
        if file:
            self.pipe._reference_file(os.path.join(self.get_path(), file))
            self.close()
        else:
            Logger.error("{} has no published files for the task {}".format(self.entity.name,
                                                                            self.ui.task_cb.currentText()))

    def browse(self):
        maya_filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;"
        file_path = cmds.fileDialog2(ds=2, cap='Open', dir=self.get_path(), ff=maya_filters, fm=1, okc='Open')
        if file_path:
            self.pipe._reference_file(file_path)
            self.close()

    def update_all_ui(self):
        self.pipe = maya_manager.MayaManager()
        types = self.pipe.settings['asset_types']
        self.ui.assetType_cb.clear()
        for type in types:
            self.ui.assetType_cb.addItem(type)

        self.update_assets()

    def update_assets(self):
        self.ui.asset_cb.clear()
        self.ui.path_le.clear()
        self.ui.versions_le.clear()
        asset_type = self.ui.assetType_cb.currentText()
        assets = self.pipe.get_assets(asset_type, base_only=True)
        self.asset_count = len(assets)
        for asset in assets:
            self.ui.asset_cb.addItem(asset)
        self.update_tasks()

    def update_tasks(self):
        self.ui.task_cb.clear()
        self.__get_asset_entity_obj()
        try:
            for task in self.entity.tasks:
                self.ui.task_cb.addItem(task)
            self.update_path_display()
        except:
            pass

    def update_path_display(self):
        self.ui.path_le.setText(self.pipe.get_relative_path(self.get_path()))
        self.update_versionCounter()

    def update_versionCounter(self):
        if self.ui.task_cb.currentText():
            self.ui.versions_le.setText(str(len(self.entity.get_rel_files(task=self.ui.task_cb.currentText()))))

    def get_path(self):
        return os.path.join(self.entity.rel_path, self.ui.task_cb.currentText())

    def __get_asset_entity_obj(self):
        asset_type = self.ui.assetType_cb.currentText()
        asset = self.ui.asset_cb.currentText()
        if asset_type and asset:
            self.entity = self.pipe.get_asset(asset, asset_type)
            return self.entity
        else:
            self.entity = None

    def on_show(self):
        new_pipe = maya_manager.MayaManager()
        if not new_pipe.current_show == self.pipe.current_show:
            self.pipe = new_pipe
            self.update_all_ui()
        self.update_versionCounter()
        asset_type = self.ui.assetType_cb.currentText()
        if self.asset_count is not len(new_pipe.get_assets(asset_type)):
            self.update_assets()
