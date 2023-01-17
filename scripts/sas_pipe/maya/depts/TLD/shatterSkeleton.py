"""
Shatter skeleton

This script will switch all skeleton parts into world space
and snap the limbs to the current pose of the joints
"""
import maya.cmds as cmds
from rigamajig2.shared import common
from rigamajig2.maya import meta
from rigamajig2.maya import transform
from rigamajig2.maya import container
from rigamajig2.maya.rig import control

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

LIMB_BONE = "limbBone"
SNAP_LOC = "shatterSnapLoc"

WORLD_SPACE = 1
LOCAL_SPACE = 0

ARMOUR_CONTROLS = ['hipArmour_l', 'hipArmour_r', 'pauldron_r', 'pauldron_l']
ORIENT_BONE_CONTROLS = ['wristBone_l', 'wristBone_r', 'ankleBone_l', 'ankleBone_r']


def run(namespace=None):
    # build a list of all the shatter controls
    shatterComponents = meta.getTagged("component", "shatterBone", namespace=namespace)
    controlsList = list()

    for component in shatterComponents:
        nodes = container.getNodesInContainer(component)
        controls = filter(control.isControl, nodes)
        controlsList += (controls)

    # add the skull control too. even though its outside the main component
    skull = "{}:skull".format(namespace) if namespace else "skull"
    if cmds.objExists(skull):
        controlsList.append(skull)

    # move a couple things to the end of the list
    for item in ORIENT_BONE_CONTROLS:
        item = "{}:{}".format(namespace, item) if namespace else item
        controlsList.append(controlsList.pop(controlsList.index(item)))

    # set the spaces for the shatter controls
    for ctl in controlsList:
        if meta.hasTag(ctl, LIMB_BONE):
            snapLimbBone(ctl)
        else:
            snapRegularBone(ctl)

    # set the armour spaces to be correct too
    for armourCtl in ARMOUR_CONTROLS:
        ctl = "{}:{}".format(namespace, armourCtl) if namespace else armourCtl
        snapRegularBone(ctl)

    # set some attributes for the rig
    setAttrs(namespace)


def snapLimbBone(boneControl, world=True):
    boneControl = common.getFirstIndex(boneControl)
    snapLoc = meta.getMessageConnection("{}.{}".format(boneControl, SNAP_LOC))

    if world:
        if cmds.objExists("{}.space".format(boneControl)):
            cmds.setAttr("{}.space".format(boneControl), WORLD_SPACE)

    if meta.hasTag(boneControl, "snapMode", "parent"):
        transform.matchTransform(snapLoc, boneControl)

    elif meta.hasTag(boneControl, "snapMode", "orient"):
        transform.matchRotate(snapLoc, boneControl)


def snapRegularBone(boneControl):
    boneControl = common.getFirstIndex(boneControl)
    if not cmds.objExists("{}.space".format(boneControl)):
        return

    # if were already in world space we can skip t
    if cmds.getAttr("{}.space".format(boneControl)) == WORLD_SPACE:
        return

    cmds.setAttr("{}.space".format(boneControl), LOCAL_SPACE)

    # create a temp locator
    tempTrs = cmds.createNode("transform", name="{}_temp_match_trs".format(boneControl))
    transform.matchTransform(boneControl, tempTrs)

    # set the control to world space and switch it
    cmds.setAttr("{}.space".format(boneControl), WORLD_SPACE)

    transform.matchTransform(tempTrs, boneControl)

    cmds.delete(tempTrs)


def setAttrs(namespace=None):
    # set the ikfkAttrs
    for ctl in ['arm_l', 'arm_r', 'leg_r', 'leg_l']:
        ctl = "{}:{}".format(namespace, ctl) if namespace else ctl

        cmds.setAttr("{}.ikfk".format(ctl), 1)
        cmds.setAttr("{}.fkMode".format(ctl), 0)

    # turn on the shatter controls
    trsShot = "{}:trs_shot".format(namespace) if namespace else "trs_shot"
    cmds.setAttr("{}.shatterControls".format(trsShot), 1)
    cmds.setAttr("{}.armour".format(trsShot), 1)
    cmds.setAttr("{}.mainControls".format(trsShot), 0)







if __name__ == '__main__':
    run()