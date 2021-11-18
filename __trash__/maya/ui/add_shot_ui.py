import os
import re

import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import __trash__.maya.maya_pipe as maya_manager
from sas_pipe import Logger

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class AddShotUI(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = AddShotUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
        cls.on_show(cls.dlg_instance)

    def __init__(self, parent=maya_main_window()):
        super(AddShotUI, self).__init__(parent)

        self.setWindowTitle("Add Shot")  # Window title name
        self.setFixedSize(270, 180)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        f = QtCore.QFile(os.path.join(os.path.join(os.path.dirname(__file__), "add_shot.ui")))
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

        self.update_all_ui()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        self.ui.seqType_cb.currentIndexChanged.connect(self.update_path_display)
        self.ui.sequence_cb.currentIndexChanged.connect(self.update_path_display)
        self.ui.shotName_le.textChanged.connect(self.update_path_display)

        self.ui.seqType_cb.currentIndexChanged.connect(self.update_seq_numbers)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.ok_btn.clicked.connect(self.ok)
        self.ui.apply_btn.clicked.connect(self.apply)

    def apply(self):
        shot_name = self.ui.shotName_le.text()
        if shot_name:
            seq_type = self.ui.seqType_cb.currentText()
            clean_name = re.sub("[0-9_{}.]", "", str(shot_name))
            seq = self.ui.sequence_cb.currentText()
            self.pipe.add_shot(sequence=seq, type=seq_type, shot=shot_name)
            self.ui.shotName_le.clear()
        else:
            Logger.warning('You must supply a shot name')

    def ok(self):
        self.apply()
        self.close()

    def update_all_ui(self):
        self.pipe = maya_manager.MayaPipeline()
        tasks = self.pipe.settings['sequence_types']
        self.ui.seqType_cb.clear()
        for task in tasks:
            self.ui.seqType_cb.addItem(task)
        self.update_seq_numbers()
        self.update_path_display()

    def update_seq_numbers(self):
        self.ui.sequence_cb.clear()
        seq_type = self.ui.seqType_cb.currentText()
        seqs = self.pipe.get_sequences(seq_type, base_only=True)
        self.ui.sequence_cb.clear()
        for seq in seqs:
            self.ui.sequence_cb.addItem(seq)

    def on_show(self):
        new_pipe = maya_manager.MayaPipeline()
        if not new_pipe.current_show == self.pipe.current_show:
            self.pipe = new_pipe
            self.update_all_ui()

    def update_path_display(self):
        path = os.path.join(self.pipe.seq_work_path, self.ui.seqType_cb.currentText(),
                            self.ui.sequence_cb.currentText(), self.ui.shotName_le.text())
        self.ui.path_le.setText(self.pipe.get_relative_path(path))
