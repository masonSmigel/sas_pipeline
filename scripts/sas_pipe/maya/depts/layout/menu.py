"""
This module creates a menu for a SAS pipeline
"""
import imp
import os
import maya.cmds as cmds
import maya.mel as mel
import sas_pipe.common as common
import sas_pipe.constants
from sas_pipe.maya.widgets import subMenuBase


class LayoutMenu(subMenuBase.SubMenu):
    def __init__(self, name='Modelling', parent=None, iconsPath=sas_pipe.constants.ICONS_PATH):
        super(LayoutMenu, self).__init__(name=name, parent=parent, iconPath=iconsPath)

    def build(self):
        """Build the layout subMenu"""

        self.addMenuItem("Quick Camera Export", command=exportCameras)


# functions explicitly connected to rigamajig2
def exportCameras(*args):
    """ Export cameras"""

    cameras = [c for c in cmds.ls("seq*") if cmds.nodeType(c) == "camera"]

    if not len(cameras) > 0:
        raise Exception("Please enusre you have at LEAST one camera following the naming convention: 'seq010_0010'. ")

    minTime = cmds.playbackOptions(q=True, min=True)
    maxTime = cmds.playbackOptions(q=True, max=True)

    # set the camera to the paybackMin
    cmds.currentTime(minTime, u=True)

    for cam in cameras:
        camTrs = cmds.listRelatives(cam, p=True)[0]

        # first create a new camera
        camToExport = cmds.duplicate(cam)
        cmds.parent(camToExport, w=True)

        # Constrain the source camera to the new camera
        camConstraint = cmds.parentConstraint(camTrs, camToExport, mo=False)

        # ... and bake it
        cmds.bakeResults(camToExport,
                         simulation=True,
                         time=(minTime, maxTime),
                         hi='none',
                         sampleBy=1,
                         oversamplingRate=1,
                         disableImplicitControl=True,
                         preserveOutsideKeys=True,
                         sparseAnimCurveBake=False,
                         removeBakedAttributeFromLayer=False,
                         removeBakedAnimFromLayer=True,
                         bakeOnOverrideLayer=False,
                         shape=False)

        cmds.delete(camConstraint)
        currentFile = cmds.file(q=True, sn=True)

        basePath = os.path.dirname(currentFile)
        savePath = r"{}/{}.fbx".format(basePath, camTrs)

        # export the camera as an fbx
        cmds.select(camToExport)
        mel.eval('FBXExport -f "{}" -s;'.format(savePath))
        print("Camera Exported to: {}".format(savePath))
        cmds.delete(camToExport)

