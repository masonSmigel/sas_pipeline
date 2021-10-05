import os

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import __trash__.maya.maya_pipe as maya_manager
import sas_pipe.utils.filenames as naming


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class OpenShotUi(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenShotUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(OpenShotUi, self).__init__(parent)

        self.setWindowTitle("Open Shot")  # Window title name
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
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "open_shot.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.update_all_ui()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.seqType_cb.currentIndexChanged.connect(self.update_sequences)
        self.ui.seq_cb.currentIndexChanged.connect(self.update_shots)
        self.ui.shot_cb.currentIndexChanged.connect(self.update_tasks)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.browse_btn.clicked.connect(self.browse)

    def ok(self):

        task = self.ui.task_cb.currentText()
        self.__get_shot_entity_obj()
        file = self.entity.get_newest_version(task=task, return_path=True)
        if file:
            self.pipe._open_file(file)
            self.close()
        else:
            res = cmds.confirmDialog(t='New Version?',
                                     m='No versions exist for {}. Would you like to save the current scene as the first version?'.format(
                                         self.entity.name),
                                     button=['No', 'Yes'], defaultButton='Yes', cancelButton='No', dismissString='No')
            if res == 'Yes':
                file = naming.get_unique_filename(base=self.entity.name,
                                                  task=task,
                                                  ext=self.pipe.settings['maya_file_type'])
                self.pipe._save_file(os.path.join(self.get_path(), file))
                self.close()

    def browse(self):
        maya_filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;"
        file_path = cmds.fileDialog2(ds=2, cap='Open', dir=self.get_path(), ff=maya_filters, fm=1, okc='Open')
        if file_path:
            self.pipe._open_file(file_path)
            self.close()

    def update_all_ui(self):
        self.pipe = maya_manager.MayaPipeline()
        types = self.pipe.settings['sequence_types']
        self.ui.seqType_cb.clear()
        for type in types:
            self.ui.seqType_cb.addItem(type)

        self.update_sequences()

    def update_sequences(self):
        self.ui.seq_cb.clear()
        seq_type = self.ui.seqType_cb.currentText()
        sequences = self.pipe.get_sequences(seq_type, base_only=True)
        self.sequences_count = len(sequences)
        for sequence in sequences:
            self.ui.seq_cb.addItem(sequence)
        self.update_shots()

    def update_shots(self):
        self.ui.shot_cb.clear()
        self.ui.path_le.clear()
        seq_type = self.ui.seqType_cb.currentText()
        seq = self.ui.seq_cb.currentText()
        shots = self.pipe.get_shots(seq, seq_type, base_only=True)
        self.shot_count = len(shots)
        for shot in shots:
            self.ui.shot_cb.addItem(shot)
        self.update_tasks()

    def update_tasks(self):
        self.ui.task_cb.clear()
        self.__get_shot_entity_obj()
        try:
            for task in self.entity.tasks:
                self.ui.task_cb.addItem(task)
        except:
            pass

    def get_path(self):
        return os.path.join(self.entity.work_path, self.ui.task_cb.currentText())

    def __get_shot_entity_obj(self):
        seq_type = self.ui.seqType_cb.currentText()
        seq = self.ui.seq_cb.currentText()
        shot = self.ui.shot_cb.currentText()
        if seq_type and seq:
            self.entity = self.pipe.find_shot(shot=shot, sequence=seq, type=seq_type)
            return self.entity
        else:
            self.entity = None

    def on_show(self):
        new_pipe = maya_manager.MayaPipeline()
        if not new_pipe.current_show == self.pipe.current_show:
            self.pipe = new_pipe
            self.update_all_ui()
        self.update_versionCounter()
        seq_type = self.ui.seqType_cb.currentText()
        seq = self.ui.seq_cb.currentText()

        if self.sequences_count is not len(new_pipe.get_sequences(seq_type, base_only=True)):
            self.update_sequences()

        if self.shot_count is not len(new_pipe.get_shots(seq, seq_type, base_only=True)):
            self.update_shots()
