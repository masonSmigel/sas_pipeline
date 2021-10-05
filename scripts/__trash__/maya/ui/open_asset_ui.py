import os

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import __trash__.maya.maya_pipe as maya_manager
import sas_pipe.utils.filenames as naming
import __trash__.show_settings as show_settings


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class OpenAssetUi(QtWidgets.QDialog):
    dlg_instance = None
    rel = False

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenAssetUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(OpenAssetUi, self).__init__(parent)

        self.setWindowTitle("Open Asset")  # Window title name
        self.setFixedSize(310, 250)  # Window minimum width

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

        self.update_all_ui()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.assetType_cb.currentIndexChanged.connect(self.assetType_changed)
        self.ui.asset_cb.currentIndexChanged.connect(self.asset_changed)
        self.ui.variant_cb.currentIndexChanged.connect(self.variant_changed)
        self.ui.task_cb.currentIndexChanged.connect(self.task_changed)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.browse_btn.clicked.connect(self.browse)

    def ok(self):
        file_info = self.entity.get_file()
        if file_info[1]:
            self.file_opperation(file_info[1])
            self.close()
        else:
            res = cmds.confirmDialog(t='New Version?',
                                     m='No versions exist for {}. '
                                       'Would you like to save the current scene as the first version?'.format(
                                         self.entity.name),
                                     button=['No', 'Yes'], defaultButton='Yes', cancelButton='No', dismissString='No')
            if res == 'Yes':
                task = self.ui.task_cb.currentText()
                ext = self.pipe.settings['maya_file_type']
                file = naming.get_unique_filename(base=self.entity.name, task=task, ext=ext)
                self.pipe._save_file(os.path.join(file_info[0], file))
                self.close()

    def browse(self):
        path = self.entity.get_file()[0]

        maya_filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;"
        file_path = cmds.fileDialog2(ds=2, cap='Open', dir=path[1], ff=maya_filters, fm=1, okc='Open')
        if file_path:
            self.pipe._open_file(file_path)
            self.close()

    def assetType_changed(self):
        self.update_assets()
        self.update_tasks()
        self.update_variants()

    def asset_changed(self):
        self.update_tasks()
        self.update_variants()

    def variant_changed(self):
        self.entity.set_variant(self.ui.variant_cb.currentText())
        self.update_display()

    def task_changed(self):
        self.entity.set_task(self.ui.task_cb.currentText())
        self.update_display()

    def update_all_ui(self):
        self.pipe = maya_manager.MayaPipeline()
        self.ui.assetType_cb.clear()
        types = show_settings.ShowSettings.get_data('asset_types')
        print types
        for type in types:
            self.ui.assetType_cb.addItem(type)

        self.update_assets()
        self.update_variants()
        self.update_tasks()

        self.entity.set_variant(self.ui.variant_cb.currentText())
        self.entity.set_task(self.ui.task_cb.currentText())
        self.update_display()

    def update_assets(self):
        self.ui.asset_cb.clear()
        self.ui.path_le.clear()
        self.ui.filename_le.clear()
        asset_type = self.ui.assetType_cb.currentText()
        assets = self.pipe.get_assets(asset_type, base_only=True)
        self.asset_count = len(assets)
        for asset in assets:
            self.ui.asset_cb.addItem(asset)

    def update_variants(self):
        self.ui.variant_cb.clear()
        self.__get_asset_entity_obj()
        print('Entity: {}, Variants: {}'.format(self.entity.name, self.entity._get_variants()))
        for variant in self.entity._get_variants():
            self.ui.variant_cb.addItem(variant)

    def update_tasks(self):
        self.ui.task_cb.clear()
        self.__get_asset_entity_obj()
        if self.entity.tasks:
            for task in self.entity.tasks:
                self.ui.task_cb.addItem(task)

    def update_display(self):

        if self.entity.task and self.entity.variant:
            file_data = self.entity.get_file()
            if file_data[0]:
                self.ui.path_le.setText(self.pipe.get_relative_path(file_data[0]))
            else:
                self.ui.path_le.setText("expected task path does not exist.")

            if file_data[1]:
                self.ui.filename_le.setText(os.path.basename(file_data[1]))
            else:
                self.ui.filename_le.setText("No Files")
        else:
            self.ui.path_le.setText('-----')
            self.ui.filename_le.setText("-----")

    def __get_asset_entity_obj(self):
        asset_type = self.ui.assetType_cb.currentText()
        asset = self.ui.asset_cb.currentText()
        if asset_type and asset:
            self.entity = self.pipe.find_asset(asset, asset_type)
            if self.rel:
                self.entity.set_mode('rel')
            else:
                self.entity.set_mode('work')
            return self.entity
        else:
            self.entity = None

    def file_opperation(self, file):
        print file 
        self.pipe._open_file(file)

    def on_show(self):
        new_pipe = maya_manager.MayaPipeline()
        if not new_pipe.current_show == self.pipe.current_show:
            self.pipe = new_pipe
            self.update_all_ui()
        asset_type = self.ui.assetType_cb.currentText()
        if self.asset_count is not len(new_pipe.get_assets(asset_type)):
            self.update_assets()
