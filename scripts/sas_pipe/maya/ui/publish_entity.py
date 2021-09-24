import os

import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe.maya.maya_pipe as maya_manager
import sas_pipe.maya.ui.quicksave as quicksave
import sas_pipe.maya.ui.widgets.function_executer as function_executer
import sas_pipe.shared.os_utils as os_utils
from sas_pipe import Logger


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class PublishEntityUi(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = PublishEntityUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(PublishEntityUi, self).__init__(parent)

        self.setWindowTitle("Publish Entity")  # Window title name
        self.setFixedSize(405, 460)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        self.pipe = maya_manager.MayaPipeline()

        self.e = self.pipe.get_entity_from_curent_file()
        self.t = self.pipe.get_task_from_current_file()

        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "publish_entity.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.tree = function_executer.FunctionExecuter()

        self.tree.load_files_from_path(os.path.join(os_utils.get_parent(__file__, 2), 'publish_steps'))

        self.ui.vBox_layout.addWidget(self.tree)
        self.ui.description_te.setMaximumHeight(80)

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.tree.tree_wid.itemSelectionChanged.connect(self.update_description)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.apply_btn.clicked.connect(self.save_and_publish)

    def ok(self):
        e = self.pipe.get_entity_from_curent_file()
        t = self.pipe.get_task_from_current_file()

        self.tree.execute_selected()
        self.pipe.publish_file(entity=e, task=t, file_type='ma')
        if self.ui.reopen_chbx.isChecked():
            self.pipe._open_file(e.get_newest_version(task=t, return_path=True))

        self.close()

    def save_and_publish(self):
        file = quicksave.QuickSave()
        self.ok()

    def update_description(self):
        self.ui.description_te.setText(self.tree.get_item_docstring())

    def on_show(self):
        e = self.pipe.get_entity_from_curent_file()
        t = self.pipe.get_task_from_current_file()
        if e:
            guess_base_name = '{}_{}'.format(e.name, t)
            path = os.path.join(e.rel_path, t, guess_base_name)
            self.ui.path_le.setText(self.pipe.get_relative_path(path))
        else:
            Logger.warning('No enitity is open. Open an entity before publishing.')
