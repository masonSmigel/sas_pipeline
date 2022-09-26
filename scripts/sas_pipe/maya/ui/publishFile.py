import os
import imp
import inspect
import re
import logging

from functools import partial

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import sas_pipe.common as common
import sas_pipe.constants
import sas_pipe.path as sas_path

import sas_pipe.maya.widgets.pathSelector as pathSelector
import sas_pipe.maya.file as sas_file

MAYA_FILTER = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"

logger = logging.getLogger(__name__)

LOCAL_TO_PUBLISH = '../publish'


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class FunctionExecuter(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(FunctionExecuter, self).__init__(*args, **kwargs)

        self.python_file = QtGui.QIcon(os.path.join(sas_pipe.constants.ICONS_PATH, "python_file.png"))
        self.python_func = QtGui.QIcon(os.path.join(sas_pipe.constants.ICONS_PATH, "python.png"))

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):

        self.tree_wid = QtWidgets.QTreeWidget()
        self.tree_wid.setIndentation(20)
        self.tree_wid.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree_wid.setHeaderHidden(True)

        self.tree_wid.setStyleSheet("QTreeView::indicator::unchecked {background-color: rgb(70, 70, 70)}"
                                    "}")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tree_wid)

    def create_connections(self):
        pass

    def add_item(self, name, data=None):
        item = QtWidgets.QTreeWidgetItem(self.tree_wid)
        item.setText(0, str(name))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        item.setData(0, QtCore.Qt.UserRole, data)
        item.setIcon(0, self.python_file)
        return item

    def add_child_item(self, parent, name, data=None):
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setText(0, str(name))
        item.setCheckState(0, QtCore.Qt.Unchecked)
        item.setData(0, QtCore.Qt.UserRole, data)
        item.setIcon(0, self.python_func)
        return item

    def load_files_from_path(self, path):
        for file in os.listdir(path):
            if not sas_path.is_file(file):
                continue

            file_type = file.split('.')[-1]
            if file_type in ['py']:
                full_path = os.path.join(path, file)
                module = imp.load_source(file.split('.')[0], full_path)

                # get all functions in a module
                all_functions = inspect.getmembers(module, inspect.isfunction)
                if len(all_functions) > 0:
                    parent = self.add_item(file, data=module)
                    for key, value in all_functions:
                        # for each function if they do not take arguments run the function
                        # if len(inspect.getargspec(value).args) < 1:
                        if not key.startswith("__"):
                            self.add_child_item(name=key, data=value, parent=parent)

    def execute_all(self):
        for i in range(self.tree_wid.topLevelItemCount()):
            file = self.tree_wid.topLevelItem(i)
            for j in range(file.childCount()):
                if file.child(j).checkState(0) == QtCore.Qt.CheckState.Checked:
                    func = file.child(j)
                    print('{}\n\t{}: '.format('-' * 80, func.text(0)))
                    func.data(0, QtCore.Qt.UserRole)()

        print('-' * 80)

    def get_item_docstring(self):
        selected_item = self.tree_wid.selectedItems()
        if selected_item:
            item = selected_item[0]
            docstring = item.data(0, QtCore.Qt.UserRole).__doc__
            if docstring:
                return re.sub(" {4}", "", docstring.strip())


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

    def __init__(self, parent=maya_main_window()):
        super(PublishEntityUi, self).__init__(parent)

        self.setWindowTitle("Publish Entity")  # Window title name
        self.setBaseSize(500, 560)  # Window minimum width

        self.setWindowFlags(QtCore.Qt.Window)  # window type

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        self.scriptJobID = -1

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.fillFeilds()

    def create_widgets(self):
        self.tree = FunctionExecuter()
        self.tree.load_files_from_path(sas_pipe.constants.PUBLISHSTEPS_PATH)

        self.discription_te = QtWidgets.QTextEdit()
        self.discription_te.setFixedHeight(100)

        self.out_file_path_selector = pathSelector.PathSelector(
            "Output File",
            caption="Select an output file",
            fileFilter=MAYA_FILTER,
            fileMode=0)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cleanup_btn = QtWidgets.QPushButton("Run Cleanup")
        self.publish_btn = QtWidgets.QPushButton("Publish")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.cleanup_btn)
        btn_layout.addWidget(self.publish_btn)

        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.out_file_path_selector)

        main_layout.addWidget(QtWidgets.QLabel("Publish Steps:"))
        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.discription_te)
        main_layout.addLayout(path_layout)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.tree.tree_wid.itemSelectionChanged.connect(self.update_description)
        self.cancel_btn.clicked.connect(self.close)
        self.cleanup_btn.clicked.connect(self.publish)
        self.publish_btn.clicked.connect(self.save_and_publish)

    def fillFeilds(self):
        """
        Auto fill the required feilds
        """
        self.out_file_path_selector.selectPath(None)

        currentFile = cmds.file(q=True, sn=True)

        if not currentFile:
            logger.warning("No file is currently open. Please save a file before attempting to publish")
            return

        basePath = os.path.dirname(currentFile)
        fileName = os.path.basename(currentFile)

        # construct a new filepath
        if not len(fileName.split("_")) == 4:
            logger.error("File is not a valid work file. Please open a SAS piped work file or check your naming convention.")
            return

        base = fileName.split("_v")[0]
        extension = fileName.split(".")[-1]

        guessFileName = "{}.{}".format(base, extension)
        guessPathName = os.path.abspath(os.path.join(basePath, LOCAL_TO_PUBLISH))
        guessFullPathName = os.path.join(guessPathName, guessFileName)

        # set the path selector locally to the current file and set the path.
        self.out_file_path_selector.setRelativePath(basePath)
        self.out_file_path_selector.selectPath(guessFullPathName)

    def publish(self):
        self.tree.execute_all()

    def save_and_publish(self):
        self.publish()

        sourceFile = cmds.file(q=True, sn=True)

        path = self.out_file_path_selector.getPath()
        if path:
            sas_file.saveAs(self.out_file_path_selector.getPath())

            # add the file the version was published from to meta-data
            self._addSourceFileToPublished(sourceFile)

            # save a versioned file
            dir_name = os.path.dirname(path)
            file_name = os.path.basename(path)

            # get the version directory, file
            version_dir = os.path.join(dir_name, 'versions')
            filebase = ".".join(file_name.split('.')[:-1])
            fileext = file_name.split('.')[-1]

            # format the new file name and file path
            version_file = "{}_{}.{}".format(filebase, 'v000', fileext)
            version_path = os.path.join(version_dir, version_file)

            # make the output directory and save the file
            sas_path.make_dir(version_dir)
            version_path = sas_file.incrimentSave(version_path, log=False)
            logger.info("out file archived: {}".format(version_path))

    def update_description(self):
        self.discription_te.setText(self.tree.get_item_docstring())

    def showEvent(self, e):
        """ override the show event to add the script job. """
        super(PublishEntityUi, self).showEvent(e)
        self.setScriptJobEnabled(True)

    def closeEvent(self, *args, **kwargs):
        super(PublishEntityUi, self).closeEvent(*args)
        self.setScriptJobEnabled(False)

    def setScriptJobEnabled(self, enabled):
        """
        Set the state of the script job.
        The script job ensures the widget displays changes when the scene changes
        """
        if enabled and self.scriptJobID < 0:
            self.scriptJobID = cmds.scriptJob(event=["SceneOpened", partial(self.fillFeilds)],
                                              protected=True)
        elif not enabled and self.scriptJobID > 0:
            cmds.scriptJob(kill=self.scriptJobID, f=True)
            self.scriptJobID = -1

    def _addSourceFileToPublished(self, file):
        """
        Add the source file as an attribute to all published nodes
        :param file: name of the source file to add as an attribute
        """
        import getpass
        from time import gmtime, strftime

        topNodes = cmds.ls(assemblies=True)

        transformNodes = cmds.ls(topNodes, exactType='transform')

        for node in transformNodes:
            shapes = cmds.listRelatives(node, s=True)
            if not shapes:
                cmds.addAttr(node, longName='__sourceFile__', dataType="string")
                cmds.setAttr("{}.{}".format(node, '__sourceFile__'), file, type="string")
                cmds.setAttr("{}.{}".format(node, '__sourceFile__'), lock=True)

                cmds.addAttr(node, longName='__publishUser__', dataType="string")
                cmds.setAttr("{}.{}".format(node, '__publishUser__'), getpass.getuser(), type="string")
                cmds.setAttr("{}.{}".format(node, '__publishUser__'), lock=True)

                cmds.addAttr(node, longName='__publishDate__', dataType="string")
                dateString = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                cmds.setAttr("{}.{}".format(node, '__publishDate__'), dateString, type="string")
                cmds.setAttr("{}.{}".format(node, '__publishDate__'), lock=True)


if __name__ == '__main__':
    import sas_pipe

    sas_pipe.reloadModule(log=False)

    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = PublishEntityUi()
    dialog.show()
