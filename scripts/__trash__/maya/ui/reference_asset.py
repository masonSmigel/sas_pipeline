import maya.OpenMayaUI as omui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import __trash__.maya.ui.open_asset_ui as open_asset_ui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ReferenceAssetUi(open_asset_ui.OpenAssetUi):
    dlg_instance = None
    rel = True

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

    def init_ui(self):
        super(ReferenceAssetUi, self).init_ui()

        self.ui.ok_btn.setText('Reference')

    def file_opperation(self, file):
        self.pipe._reference_file(file)