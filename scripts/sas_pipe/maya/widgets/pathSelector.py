"""
This module contains the file selector widget
"""
import os

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import maya.cmds as cmds

from sas_pipe.maya.ui import showInFolder


class PathSelector(QtWidgets.QWidget):
    """ Widget to select valid file or folder paths """

    def __init__(self,
                 label=None,
                 caption='Select a file or Folder',
                 fileFilter="All Files (*.*)",
                 fileMode=1,
                 relativePath=None,
                 parent=None):
        super(PathSelector, self).__init__(parent)
        self.caption = caption
        self.fileFilter = fileFilter
        self.fileMode = fileMode
        self.relativePath = relativePath
        self.label = label

        self.pathLabel = QtWidgets.QLabel()

        self.pathLineEdit = QtWidgets.QLineEdit()
        self.pathLineEdit.setPlaceholderText("path/to/file/or/folder")

        self.selectPathButton = QtWidgets.QPushButton("...")
        self.selectPathButton.setFixedSize(24, 19)
        self.selectPathButton.setToolTip(self.caption)
        self.selectPathButton.clicked.connect(self.pickPath)

        self.showInFolderButton = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.showInFolderButton.setFixedSize(24, 19)
        self.showInFolderButton.setToolTip("Show in Folder")
        self.showInFolderButton.clicked.connect(self.showInFolder)

        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(4)
        if self.label is not None:
            self.mainLayout.addWidget(self.pathLabel)
            self.setLabelText(self.label)
            self.pathLabel.setFixedWidth(60)

        self.mainLayout.addWidget(self.pathLineEdit)
        self.mainLayout.addWidget(self.selectPathButton)
        self.mainLayout.addWidget(self.showInFolderButton)

    def setPath(self, path):
        """ Set the widgets path"""
        self.pathLineEdit.setText(path)

    def pickPath(self, path=None):
        """
        Pick a path from the file selector
        :param path:
        :return:
        """
        currentPath = self.getPath(absoultePath=True)

        if not path:
            fileInfo = QtCore.QFileInfo(currentPath)
            if not fileInfo.exists():
                currentPath = cmds.workspace(q=True, dir=True)

            newPath = cmds.fileDialog2(
                ds=2,
                cap=self.caption,
                ff=self.fileFilter,
                fm=self.fileMode,
                okc='Select',
                dir=currentPath
                )
            if newPath:
                newPath = newPath[0]
            else:
                # if we dont select a new path cancel the action by returning.
                return
            # next select the new path.
            self.selectPath(newPath)

    def selectPath(self, path=None):
        """
        Select an existing path. this is smarter than set path because it will create a dailog and check if the path exists.
        :param path:
        :return:
        """
        if path is None:
            self.pathLineEdit.setText('')
            return

        if path:
            # here we can check if there is a set relative path and set it properly.
            # if the newPath is not absoulte we can skip this
            if self.relativePath and os.path.isabs(path):
                path = os.path.relpath(path, self.relativePath)
            self.pathLineEdit.setText(path)

    def showInFolder(self):
        """ show the given file in the enclosing folder"""
        filePath = self.getPath()
        showInFolder.showInFolder(filePath=filePath)

    def getPath(self, absoultePath=True):
        """
        Get the path of the widget.
        if a relative path is set get the absoulte path
        """

        if self.pathLineEdit.text():
            if self.relativePath and absoultePath:
                return os.path.abspath(os.path.join(self.relativePath, self.pathLineEdit.text()))
            else:
                return self.pathLineEdit.text()

    def setRelativePath(self, relativeTo):
        """ Set the path display relative to a folder """
        self.relativePath = relativeTo

    def setLabelText(self, text):
        """ Set the label text"""
        self.pathLabel.setText(text)
