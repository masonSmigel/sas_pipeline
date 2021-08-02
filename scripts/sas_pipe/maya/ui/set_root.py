import os

from PySide2 import QtWidgets

import sas_pipe.maya.maya_manager as maya_manager
from sas_pipe.shared.logger import Logger


def run():
    filename = QtWidgets.QFileDialog.getExistingDirectory(caption='Select a root for SAS Pipeline',
                                                          directory=os.getcwd())

    if os.path.exists(filename):
        maya_manager.MayaManager.set_root_path(filename)
        maya_manager.MayaManager.validate_root(log=True)
        return filename
    else:
        Logger.error("path {} does not exist".format(filename))
