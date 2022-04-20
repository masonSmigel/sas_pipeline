""" This module contains publish steps for models"""


import maya.cmds as cmds


def deleteDisplayLayers():
    """
    Delete all display layers within the current scene.
    This will not affects objects within display layers
    """

    for layer in cmds.ls(long=True, type='displayLayer'):
        if layer == 'defaultLayer':
            continue
        cmds.delete(layer)
        print("removed display layer: {}".format(layer))


def __isMesh(node):
    """
    check if the node is a mesh
    :param node: node to check
    :return:
    """
    if not cmds.objExists(node): return False
    if 'transform' in cmds.nodeType(node, i=True):
        shape = cmds.ls(cmds.listRelatives(node, s=True, ni=True, pa=True) or [], type='mesh')
        if not shape: return False
        node = shape[0]
    if cmds.objExists(cmds.objExists(node) != 'mesh'): return False
    return True


def __cleanShapes(nodes):
    """
    Cleanup a shape nodes. removes intermediate
    :param nodes:
    :return:
    """

    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]
    for node in nodes:
        if cmds.nodeType(node) in ['nurbsSurface', 'mesh', 'nurbsCurve']:
            node = cmds.listRelatives(node, p=True)
        shapes = cmds.listRelatives(node, s=True, ni=False, pa=True) or []

        if len(shapes) == 1:
            return shapes[0]
        else:
            intermidiate_shapes = [x for x in shapes if cmds.getAttr('{}.intermediateObject'.format(x))]
            cmds.delete(intermidiate_shapes)
            print("Deleted Intermeidate Shapes: {}".format(intermidiate_shapes))


def cleanModel():
    """
    Run Cleanup opperations on the selected models.
    This includes: freezing Transformation, Deleting Construction history and Removing unnessary shape nodes.
    """

    nodes = cmds.ls(sl=True)

    for node in nodes:
        cmds.delete(node, ch=True)

        # unlock all keyable channels
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
            cmds.setAttr("{}.{}".format(node, attr), l=False)

        cmds.makeIdentity(node, apply=True, t=True, r=True, s=True, n=0, pn=1)
        cmds.xform(node, a=True, ws=True, rp=(0, 0, 0), sp=(0, 0, 0))
        if __isMesh(node):
            __cleanShapes(node)
            print('Cleaned Mesh: {}'.format(node))
