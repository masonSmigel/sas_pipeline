"""
This module contains the asset browser UI
"""
import sys, os, json, subprocess, platform
import logging
from collections import OrderedDict

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import sas_pipe.common as common
import sas_pipe.api.cmds as sas
import sas_pipe.constants
import sas_pipe.environment as environment
from sas_pipe.entities import studio, show, sequence, shot, element
import sas_pipe.maya.file as maya_file
import sas_pipe.api.cmds as sas_cmds
from sas_pipe.maya.ui import showInFolder

logger = logging.getLogger(__name__)


class SAS_EntityInfo(QtWidgets.QWidget):
    VARIANT_WGDTS = list()
    BLANK_IMAGE = os.path.join(sas_pipe.constants.ICONS_PATH, "blankImage.png")

    def __init__(self):
        super(SAS_EntityInfo, self).__init__()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.current_entity = None
        self.current_item_path = None

    def create_widgets(self):
        self.icon = QtWidgets.QLabel("")
        self.entity_name_la = QtWidgets.QLabel("")

        custom_font = QtGui.QFont()
        custom_font.setPointSize(14)
        self.entity_name_la.setFont(custom_font)

        self.thumbnail_la = QtWidgets.QLabel()
        self.capture_thumbnail_action = QtWidgets.QAction("Capture Thumbnail")
        self.capture_thumbnail_action.triggered.connect(self.capture_thumbnail)

        self.thumbnail_la.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.thumbnail_la.addAction(self.capture_thumbnail_action)

        self.info_te = QtWidgets.QTextEdit()
        self.info_te.setReadOnly(True)

        self.task_cb = QtWidgets.QComboBox()
        self.task_cb.setMinimumWidth(180)
        self.task_cb.setMinimumHeight(30)
        self.task_cb.setMaxVisibleItems(30)

        self.task_te = QtWidgets.QTextEdit()
        self.task_te.setReadOnly(True)
        self.task_te.resize(self.task_te.sizeHint().width(), 100)

        # self.open_varant_mgr_btn = QtWidgets.QPushButton("Open Variant Manager")
        self.open_work_btn = QtWidgets.QPushButton("Open (Work File)")
        self.open_work_btn.setMinimumHeight(30)

        self.open_publish_btn = QtWidgets.QPushButton("Open (Publish File)")
        self.open_publish_btn.setMinimumHeight(30)

        self.import_publish_btn = QtWidgets.QPushButton("Import (Publish File)")
        self.import_publish_btn.setMinimumHeight(30)

        self.reference_publish_btn = QtWidgets.QPushButton("Reference (Publish File)")
        self.reference_publish_btn.setMinimumHeight(30)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        entity_layout = QtWidgets.QHBoxLayout()
        entity_layout.addWidget(QtWidgets.QLabel("Entity:"))

        thumbnail_layout = QtWidgets.QHBoxLayout()
        thumbnail_layout.addWidget(self.thumbnail_la)
        thumbnail_layout.addStretch()

        self.main_layout.addLayout(thumbnail_layout)
        entity_layout.addWidget(self.entity_name_la)
        entity_layout.addStretch()

        self.main_layout.addLayout(entity_layout)
        self.main_layout.addWidget(self.info_te)

        open_layout = QtWidgets.QVBoxLayout()
        taskLayout = QtWidgets.QHBoxLayout()
        taskLayout.addWidget(QtWidgets.QLabel("Task:"))
        taskLayout.addWidget(self.task_cb)

        open_layout.addLayout(taskLayout)
        open_layout.addWidget(self.task_te)
        open_layout.addWidget(self.open_work_btn)
        open_layout.addWidget(self.open_publish_btn)
        open_layout.addWidget(self.import_publish_btn)
        open_layout.addWidget(self.reference_publish_btn)
        self.main_layout.addLayout(open_layout)

    def create_connections(self):
        self.task_cb.currentIndexChanged.connect(self.update_task_data)
        self.open_work_btn.clicked.connect(self.open_file)
        self.open_publish_btn.clicked.connect(self.open_publish_file)
        self.import_publish_btn.clicked.connect(self.import_file)
        self.reference_publish_btn.clicked.connect(self.reference_file)
        # self.variant_cb.currentIndexChanged.connect(self.update_variant_data)

    def set_item(self, item_path):
        file_info = QtCore.QFileInfo(item_path)

        self.current_entity = self._find_entity(file_info.filePath())
        self.current_item_path = file_info.filePath()
        old_task = self.task_cb.currentText()

        self.info_te.clear()
        self.task_cb.clear()
        self.task_te.clear()

        if self.current_entity:
            # edit the main file info
            self.entity_name_la.setText(self.current_entity.name)

            # read the manifest file so we can grab some data from there
            manifest_file_info = QtCore.QFileInfo(self.current_entity.manifest_path)
            f = open(manifest_file_info.filePath(), 'r')
            if sys.version_info.major == 3:
                data = json.loads(f.read(), object_pairs_hook=OrderedDict)
            else:
                data = json.loads(f.read().decode('utf-8'), object_pairs_hook=OrderedDict)
            f.close()

            self.info_te.append("entity type: {}".format(self.current_entity.type))
            self.info_te.append("{}: created".format(manifest_file_info.created().toString("yyyy-MM-dd hh:mm:ss")))
            self.info_te.append("{}: modified".format(data['time']))
            self.info_te.append("modified by: {}".format(data['user']))
            self.thumbnail_la.setPixmap(None)

            if self.current_entity.type in ['Studio', 'Show']:
                pass
            if self.current_entity.type in ["Element", 'Shot']:
                for task in self.current_entity.get_tasks():
                    self.task_cb.addItem(task)
                self.task_cb.adjustSize()

                # setup some task info
                self.update_task_data()

                if old_task:
                    try:
                        index = self.task_cb.findText(old_task, QtCore.Qt.MatchFixedString)
                        self.task_cb.setCurrentIndex(index)
                    except:
                        self.task_cb.setCurrentIndex(0)

                # check for a thumbnail. if we dont have one use the default blank image icon
                if os.path.exists(self.current_entity.get_thumbnail_path()):
                    thumbnail = self.current_entity.get_thumbnail_path()
                else:
                    thumbnail = self.BLANK_IMAGE
                self.update_thumbnail(thumbnail)

    def _find_entity(self, item_path):
        # look if the current shot is an entity
        if element.isElement(item_path):
            return element.Element(item_path)
        elif shot.isShot(item_path):
            return shot.Shot(item_path)
        elif show.isShow(item_path):
            return show.Show(item_path)
        elif studio.isstudio(item_path):
            return studio.Studio(item_path)
        # if its not one of these then we can check the directory up
        else:
            parent_path = os.path.realpath(os.path.join(item_path, ".."))
            return self._find_entity(parent_path)

    def update_thumbnail(self, image_path):
        if not os.path.exists(image_path):
            return

        img = QtGui.QImage(image_path)
        pixmap = QtGui.QPixmap(img.scaledToWidth(128))
        pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        self.thumbnail_la.setScaledContents(True)
        self.thumbnail_la.setPixmap(pixmap)

    def update_task_data(self):
        # setup some task info
        self.task_te.clear()

        if self.task_cb.currentText() == '':
            return

        publishedFiles = self.current_entity.get_publish_files(self.task_cb.currentText())
        versionFiles = self.current_entity.get_publish_version_files(self.task_cb.currentText())
        workFiles = self.current_entity.get_work_files(self.task_cb.currentText())

        self.task_te.append("published file: {}".format("True" if len(publishedFiles) > 0 else "False"))
        self.task_te.append("published versions: {}".format(len(versionFiles)))
        self.task_te.append("work versions: {}".format(len(workFiles)))

    def capture_thumbnail(self):
        """ do a thumbnial capture"""
        entity = self._find_entity(self.current_item_path)
        thumbnail_path = entity.get_thumbnail_path()

        current_time = cmds.currentTime(q=True)
        cmds.playblast(p=100, w=512, h=512, framePadding=0, st=current_time, et=current_time,
                       viewer=False, forceOverwrite=True, orn=False,
                       format="image", compression="jpg", cf=thumbnail_path)

        self.update_thumbnail(entity.get_thumbnail_path())

    def open_file(self):
        """
        Open a work file
        :return:
        """
        task = self.task_cb.currentText()
        workFiles = self.current_entity.get_work_files(task, fileTypes=['ma', 'mb'])

        # if we dont have any work files return
        if len(workFiles) < 1:
            return

        # Sort the files to get the file with the greatest idex
        sortedFiles = sorted(workFiles)

        # compose the full path
        fullPath = self.current_entity.compose_path(task, sas_pipe.constants.WORK_TOKEN, fileName=sortedFiles[-1])

        maya_file.open_(fullPath, f=True)

    def open_publish_file(self):
        """
        Open a work file
        :return:
        """
        task = self.task_cb.currentText()
        publishFiles = self.current_entity.get_publish_files(task, fileTypes=['ma', 'mb'])

        # if we dont have any work files return
        if len(publishFiles) < 1:
            publishFiles = self.current_entity.get_work_files(self.task_cb.currentText(), fileTypes=['ma', 'mb'])

        # Sort the files to get the file with the greatest idex
        sortedFiles = sorted(publishFiles)

        fullPath = self.current_entity.compose_path(task, sas_pipe.constants.REL_TOKEN, fileName=sortedFiles[-1])
        maya_file.open_(fullPath, f=True)

    def import_file(self):
        """
        Open a work file
        :return:
        """
        task = self.task_cb.currentText()
        publishFiles = self.current_entity.get_publish_files(task, fileTypes=['ma', 'mb'])

        # if we dont have any work files return
        if len(publishFiles) < 1:
            publishFiles = self.current_entity.get_work_files(self.task_cb.currentText(), fileTypes=['ma', 'mb'])

        # Sort the files to get the file with the greatest idex
        sortedFiles = sorted(publishFiles)

        fullPath = self.current_entity.compose_path(task, sas_pipe.constants.REL_TOKEN, fileName=sortedFiles[-1])
        maya_file.import_(fullPath, useNamespace=True, force=True)

    def reference_file(self):
        """
        Open a work file
        :return:
        """
        task = self.task_cb.currentText()
        publishFiles = self.current_entity.get_publish_files(task, fileTypes=['ma', 'mb'])

        # if we dont have any work files return
        if len(publishFiles) < 1:
            publishFiles = self.current_entity.get_work_files(self.task_cb.currentText(), fileTypes=['ma', 'mb'])

        # Sort the files to get the file with the greatest idex
        sortedFiles = sorted(publishFiles)

        fullPath = self.current_entity.compose_path(task, sas_pipe.constants.REL_TOKEN, fileName=sortedFiles[-1])
        maya_file.reference(fullPath, )


class SAS_AssetBrowser(QtWidgets.QDialog):
    WINDOW_TITLE = "SAS Entity Browser"
    dlg_instance = None

    mkelm_instance = None
    mkshot_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = SAS_AssetBrowser()

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

        super(SAS_AssetBrowser, self).__init__(maya_main_window)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setProperty("saveWindowPref", True)
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(900, 225)
        self.resize(1000, 650)

        self.create_actions()
        self.create_menus()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.initalize_ui()

    def create_actions(self):
        # CREATE
        self.create_elm_action = QtWidgets.QAction("Create Element", self)
        self.create_elm_action.triggered.connect(self.create_elm)
        self.create_shot_action = QtWidgets.QAction("Create Shot", self)
        self.create_shot_action.triggered.connect(self.create_shot)

        self.update_tasks_action = QtWidgets.QAction("Update Tasks", self)
        self.update_tasks_action.triggered.connect(self.update_tasks)

        # TOOLS
        self.flush_env_action = QtWidgets.QAction("Flush Environment", self)
        self.flush_env_action.triggered.connect(environment.flushEnv)

    def create_menus(self):
        self.main_menu = QtWidgets.QMenuBar()

        create_menu = self.main_menu.addMenu("Create")
        create_menu.addAction(self.create_elm_action)
        create_menu.addAction(self.create_shot_action)
        create_menu.addAction(self.update_tasks_action)

        tools_menu = self.main_menu.addMenu("Tools")
        tools_menu.addAction(self.flush_env_action)

    def create_widgets(self):
        # self.studio_path_le = QtWidgets.QLineEdit()
        # self.studio_path_le.setPlaceholderText("studio/...")

        self.set_studio_btn = QtWidgets.QPushButton("...")
        self.set_studio_btn.setFixedWidth(30)

        self.studio_cb = QtWidgets.QComboBox()
        self.studio_cb.setFixedWidth(400)
        self.studio_cb.setFixedHeight(25)

        self.show_cb = QtWidgets.QComboBox()
        self.show_cb.setFixedWidth(120)
        self.display_show_only = QtWidgets.QCheckBox("current show only")
        self.display_show_only.setChecked(True)

        # add the file system and tree view
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath((QtCore.QDir.rootPath()))
        self.browser_tree = QtWidgets.QTreeView()
        self.browser_tree.setModel(self.model)

        self.browser_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.browser_tree.customContextMenuRequested.connect(self.context_menu)

        # stuff for the navigate browser
        self.search_icon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(os.path.join(sas_pipe.constants.ICONS_PATH, "search.png"))
        self.search_icon.setScaledContents(True)
        self.search_icon.setPixmap(pixmap)

        self.search_bar_le = QtWidgets.QLineEdit()
        self.search_bar_le.setPlaceholderText("search for an entity")

        # Set browser sorting
        self.browser_tree.setIndentation(30)
        self.browser_tree.setSortingEnabled(True)
        self.browser_tree.sortByColumn(2, QtCore.Qt.AscendingOrder)  # sort by the kind
        self.browser_tree.setColumnWidth(0, 300)
        self.browser_tree.setRootIsDecorated(True)

        self.entity_info_wdgt = SAS_EntityInfo()

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setMenuBar(self.main_menu)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        self.show_grp = QtWidgets.QGroupBox()
        self.show_grp.setFixedHeight(50)
        show_layout = QtWidgets.QHBoxLayout()

        show_layout.addWidget(QtWidgets.QLabel("Studio: "))
        show_layout.addWidget(self.studio_cb)
        show_layout.addWidget(self.set_studio_btn)
        show_layout.addStretch(100)

        show_layout.addSpacing(25)
        show_layout.addWidget(QtWidgets.QLabel("Show: "))
        show_layout.addWidget(self.show_cb)
        show_layout.addSpacing(25)
        show_layout.addWidget(self.display_show_only)

        self.show_grp.setLayout(show_layout)

        self.browser_grp = QtWidgets.QGroupBox('File Browser')
        self.entity_info_grp = QtWidgets.QGroupBox('Entity Info')
        self.entity_info_grp.setMaximumWidth(300)

        searchbar_layout = QtWidgets.QHBoxLayout()
        searchbar_layout.addWidget(self.search_icon)
        searchbar_layout.addWidget(self.search_bar_le)

        browser_layout = QtWidgets.QVBoxLayout()
        browser_layout.addLayout(searchbar_layout)
        browser_layout.addWidget(self.browser_tree)

        entity_layout = QtWidgets.QVBoxLayout()
        entity_layout.addWidget(self.entity_info_wdgt)

        entities_layout = QtWidgets.QHBoxLayout()

        self.browser_grp.setLayout(browser_layout)
        self.entity_info_grp.setLayout(entity_layout)

        browser_splitter = QtWidgets.QSplitter()
        browser_splitter.setCollapsible(0, True)
        browser_splitter.setCollapsible(1, True)
        browser_splitter.setOrientation(QtCore.Qt.Horizontal)
        entities_layout.addWidget(browser_splitter)

        browser_splitter.addWidget(self.browser_grp)
        browser_splitter.addWidget(self.entity_info_grp)
        browser_splitter.setStretchFactor(0, 6)
        browser_splitter.setStretchFactor(1, 2)

        # add groups to main layout
        main_layout.addWidget(self.show_grp)
        main_layout.addLayout(entities_layout)

    def create_connections(self):
        self.set_studio_btn.clicked.connect(self.change_studio)
        self.studio_cb.currentIndexChanged.connect(self.changeComboboxStudio)
        self.show_cb.currentIndexChanged.connect(self.change_show)
        self.display_show_only.clicked.connect(self.update_show)
        self.search_bar_le.returnPressed.connect(self.search_for_entity)
        self.browser_tree.selectionModel().selectionChanged.connect(self.update_display)

    def context_menu(self):
        menu = QtWidgets.QMenu()
        self.open_file_action = QtWidgets.QAction("Open", self)
        self.open_file_action.triggered.connect(self.open_file)

        self.import_file_action = QtWidgets.QAction("Import", self)
        self.import_file_action.triggered.connect(self.import_file)

        self.reference_file_action = QtWidgets.QAction("Reference", self)
        self.reference_file_action.triggered.connect(self.reference_file)

        self.show_in_folder_action = QtWidgets.QAction("Show in Folder", self)
        self.show_in_folder_action.setIcon(QtGui.QIcon(":folder-open.png"))
        self.show_in_folder_action.triggered.connect(self.show_in_folder)

        menu.addAction(self.open_file_action)
        menu.addAction(self.import_file_action)
        menu.addAction(self.reference_file_action)
        menu.addSeparator()
        menu.addAction(self.show_in_folder_action)
        menu.addSeparator()

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    # --------------------------------------------------------------------------------
    # Browser functionality
    # --------------------------------------------------------------------------------

    def initalize_ui(self):
        """update the ui with new functionality"""
        sas.initenv(silent=True)

        currentStudio = sas.getstudio()

        # add the studio swap ui
        for studio in sas.getstudios():
            self.studio_cb.addItem(studio)

        index = self.studio_cb.findText(currentStudio, QtCore.Qt.MatchFixedString)
        self.studio_cb.setCurrentIndex(index)

        self.update_studio(currentStudio)

    def changeComboboxStudio(self):
        """ Change the name of the studio"""
        currentStudio = self.studio_cb.currentText()

        sas.setstudio(currentStudio)
        self.update_studio(currentStudio)

    def update_studio(self, studio):
        """update the UI to reflect a studio change"""
        sas.initenv(silent=True)

        # if we dont have a studio return.
        if not sas.getstudio():
            return
        shows = sas.lsshow()
        current_show = sas.getshow()

        # clear all current shows
        self.show_cb.clear()

        # all shows in the studio
        for show in shows:
            self.show_cb.addItem(show)

        if current_show:
            index = self.show_cb.findText(current_show, QtCore.Qt.MatchFixedString)
            if index >= 0: self.show_cb.setCurrentIndex(index)

        self.entity_info_wdgt.set_item(studio)

    def update_show(self, show):
        """update the UI to reflect a show change"""
        if self.display_show_only.isChecked():
            self.browser_tree.setRootIndex(self.model.index(environment.getEnv('show_path')))
        else:
            self.browser_tree.setRootIndex(self.model.index(environment.getEnv('root')))

    def update_display(self):

        selected_item = self.get_selected_file()
        if selected_item:
            self.entity_info_wdgt.set_item(selected_item)

    def open_file(self):
        path = self.get_selected_file()

        filename, file_extension = os.path.splitext(path)
        if file_extension in ['.ma', '.mb']:
            maya_file.open_(path, f=True)
        else:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(path)
            else:  # linux variants
                subprocess.call(('xdg-open', path))

    def import_file(self):
        path = self.get_selected_file()

        filename, file_extension = os.path.splitext(path)
        if file_extension in ['.ma', '.mb']:
            maya_file.import_(path, useNamespace=True, namespace=None, force=True)
        else:
            logger.error("Cannot import files other than maya files")

    def reference_file(self):
        path = self.get_selected_file()

        filename, file_extension = os.path.splitext(path)
        if file_extension in ['.ma', '.mb']:
            maya_file.reference(path)
        else:
            logger.error("Cannot import files other than maya files")

    # --------------------------------------------------------------------------------
    # Browser connections
    # --------------------------------------------------------------------------------
    def change_studio(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Studio Root')
        if path:
            sas.setstudio(path)
            self.update_studio(path)
            self.studio_cb.addItem(path)

            index = self.studio_cb.findText(path, QtCore.Qt.MatchFixedString)
            self.studio_cb.setCurrentIndex(index)

            sas.setstudio(path)
            self.update_studio(path)

    def change_show(self):
        show = self.show_cb.currentText()
        sas.setshow(show=show)
        self.update_show(show)

    def search_for_entity(self):

        entity_code = self.search_bar_le.text()

        # check if this is an element
        entity_path = sas.nelm(entity_code)

        if not entity_path:
            seq, shot = entity_code.split(" ")
            entity_path = sas.nshot(seq, shot)
            # if len(entity_code.split(' ')) >= 2:
            #     seq, shot = entity_code.split(' ')[:2]
            #     entity_path = sas.nshot(seq, shot)
        print(entity_path)

        if entity_path:
            index = self.model.index(entity_path)
            print(entity_path)
            self.entity_info_wdgt.set_item(self.model.filePath(index))
            self.browser_tree.selectionModel().select(index, QtCore.QItemSelectionModel.ClearAndSelect)

            # expand the tree widget to the item
            while index.parent().isValid():
                index = index.parent()
                self.browser_tree.expand(index)

    def get_selected_file(self):
        indexes = self.browser_tree.selectedIndexes()
        for index in indexes:
            # get selected column.
            if index.column() != 1:
                continue
            return self.model.filePath(index)

    # --------------------------------------------------------------------------------
    # Browser Utilities
    # --------------------------------------------------------------------------------
    def show_in_folder(self):
        file_path = self.get_selected_file()
        showInFolder.showInFolder(file_path)

    def create_elm(self):
        CreateElementDialog().exec_()

    def create_shot(self):
        CreateShotDialog().exec_()

    def update_tasks(self):
        sas.updateelm()
        sas.updateshot()


class CreateElementDialog(QtWidgets.QDialog):
    WINDOW_TITLE = "Create an Element"

    def __init__(self):
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        else:
            maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

        super(CreateElementDialog, self).__init__(maya_main_window)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setProperty("saveWindowPref", True)
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setFixedSize(375, 75)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.elm_type_la = QtWidgets.QLabel("Type:")
        self.elm_type_la.setFixedWidth(30)
        self.elm_type_cb = QtWidgets.QComboBox()

        show_enitity = show.Show(environment.getEnv("show_path"))
        for type in show_enitity.get_elementTypes():
            self.elm_type_cb.addItem(type)

        self.name_la = QtWidgets.QLabel("Name:")
        self.name_la.setFixedWidth(30)
        self.name_le = QtWidgets.QLineEdit()

        self.create_btn = QtWidgets.QPushButton("Create")
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        elm_type_layout = QtWidgets.QHBoxLayout()
        elm_type_layout.addWidget(self.elm_type_la)
        elm_type_layout.addWidget(self.elm_type_cb)
        elm_type_layout.addSpacing(20)
        elm_type_layout.addWidget(self.name_la)
        elm_type_layout.addWidget(self.name_le)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.create_btn)

        main_layout.addLayout(elm_type_layout)
        # main_layout.addWidget(self.variant_te)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.cancel_btn.clicked.connect(self.close)
        self.apply_btn.clicked.connect(self.apply)
        self.create_btn.clicked.connect(self.create)

    def apply(self):
        elm_type = self.elm_type_cb.currentText()
        elm_name = self.name_le.text()

        if not elm_name:
            logger.error("Must provide an element name")
            return

        elm = sas_cmds.mkelm(elm_name, elm_type)
        print("{}\nCreated New Element\n{}".format("-" * 80, "-" * 80))
        print(elm)
        print("-" * 80)

    def create(self):
        self.apply()
        self.close()

    def clear(self):
        self.name_le.clear()


class CreateShotDialog(CreateElementDialog):
    WINDOW_TITLE = "Create a Shot"

    def __init__(self):
        super(CreateShotDialog, self).__init__()

    def create_widgets(self):
        self.elm_type_la = QtWidgets.QLabel("Type:")
        self.elm_type_la.setFixedWidth(30)
        self.elm_type_cb = QtWidgets.QComboBox()

        show_enitity = show.Show(environment.getEnv("show_path"))
        for type in show_enitity.get_sequenceTypes():
            self.elm_type_cb.addItem(type)

        index = self.elm_type_cb.findText(show_enitity.get_sequenceTypes()[-1], QtCore.Qt.MatchFixedString)
        self.elm_type_cb.setCurrentIndex(index)

        self.seq_la = QtWidgets.QLabel("Seq:")
        self.seq_la.setFixedWidth(30)
        self.seq_le = QtWidgets.QLineEdit()

        self.shot_la = QtWidgets.QLabel("Shot:")
        self.shot_la.setFixedWidth(30)
        self.shot_le = QtWidgets.QLineEdit()

        self.create_btn = QtWidgets.QPushButton("Create")
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        elm_type_layout = QtWidgets.QHBoxLayout()
        elm_type_layout.addWidget(self.elm_type_la)
        elm_type_layout.addWidget(self.elm_type_cb)
        elm_type_layout.addSpacing(20)
        elm_type_layout.addWidget(self.seq_la)
        elm_type_layout.addWidget(self.seq_le)
        elm_type_layout.addSpacing(20)
        elm_type_layout.addWidget(self.shot_la)
        elm_type_layout.addWidget(self.shot_le)

        # path_layout = QtWidgets.QHBoxLayout()
        # path_layout.addWidget(self.path_la)
        # path_layout.addWidget(self.path_le)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.create_btn)

        main_layout.addLayout(elm_type_layout)
        main_layout.addLayout(btn_layout)

    def apply(self):
        seq_type = self.elm_type_cb.currentText()
        seq_name = self.seq_le.text()
        shot_name = self.shot_le.text()

        if not seq_name and not shot_name:
            logger.error("Must provide a Sequence and Shot name")
            return

        shot = sas_cmds.mkshot(seq_name, shot_name, seq_type)
        print("{}\nCreated New Shot\n{}".format("-" * 80, "-" * 80))
        print(shot)
        print("-" * 80)

    def clear(self):
        self.seq_le.clear()
        self.shot_le.clear()


if __name__ == '__main__':
    import sas_pipe

    sas_pipe.reloadModule(log=False)

    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = SAS_AssetBrowser()
    dialog.show()
