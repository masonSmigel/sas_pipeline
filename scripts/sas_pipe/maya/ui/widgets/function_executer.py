""" Custom Python function widget """
import imp
import inspect
import os
import re

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import sas_pipe.shared.os_utils as dir
import sas_pipe.shared.common as common
from sas_pipe.shared.logger import Logger


class FunctionExecuter(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(FunctionExecuter, self).__init__(*args, **kwargs)

        self.python_file = QtGui.QIcon(os.path.join(common.ICONS_PATH, "python_file.png"))
        self.python_func = QtGui.QIcon(os.path.join(common.ICONS_PATH, "python.png"))

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):

        self.tree_wid = QtWidgets.QTreeWidget()
        self.tree_wid.setIndentation(20)
        self.tree_wid.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        header = self.tree_wid.headerItem()
        header.setText(0, "Publish Steps")

        self.tree_wid.setStyleSheet("QTreeView {background-color: rgb(73, 73, 73)}"
                                    "QTreeView::indicator::unchecked {background-color: rgb(30, 30, 30)}"
                                    "}")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
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
        for file in dir.get_contents(path=path, dirs=False, files=True):
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
                        if len(inspect.getargspec(value).args) < 1:
                            self.add_child_item(name=key, data=value, parent=parent)

    def execute_selected(self):

        for i in range(self.tree_wid.topLevelItemCount()):
            file = self.tree_wid.topLevelItem(i)
            for j in range(file.childCount()):
                if file.checkState(j):
                    func = file.child(j)
                    try:
                        func.data(0, QtCore.Qt.UserRole)()
                        Logger.info('Sucessful Process: {}'.format(func.text(0)))
                    except:
                        Logger.error('Failed to Process: {}'.format(func.text(0)))

    def get_item_docstring(self):
        selected_item = self.tree_wid.selectedItems()
        if selected_item:
            item = selected_item[0]
            docstring = item.data(0, QtCore.Qt.UserRole).__doc__
            if docstring:
                return re.sub(" {4}", "", docstring.strip())
