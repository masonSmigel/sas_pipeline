import os

from PySide2 import QtWidgets

import sas_pipe.maya.maya_pipe as maya_manager
from sas_pipe.shared.logger import Logger
import maya.cmds as cmds


def run():
    # filename = QtWidgets.QFileDialog.getExistingDirectory(caption='Select a root for SAS Pipeline',
    #                                                       directory=os.getcwd())
    #
    # if os.path.exists(filename):
    #     maya_manager.MayaManager.set_root_path(filename)
    #     maya_manager.MayaManager.validate_root(log=True)
    #     return filename
    # else:
    #     Logger.error("path {} does not exist".format(filename))

    filename = cmds.fileDialog2(cap='Select a root for SAS Pipeline',
                                ds=2,
                                fileMode=2,
                                okCaption="Set Root")
    print "Dialog Results:", filename

    if filename:
        if os.path.exists(filename[0]):
            maya_manager.MayaPipeline.set_root_path(filename[0])
            maya_manager.MayaPipeline.validate_root(log=True)
            return filename[0]
        else:
            Logger.error("path {} does not exist".format(filename))
