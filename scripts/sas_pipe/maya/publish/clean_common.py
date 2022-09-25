""" This module contains publish steps for genreal functions"""
import maya.cmds as cmds


BAD_NODES = ['breed_gene', 'vaccine_gene']


def cleanVirus():
    """
    remove the maya virus script nodes from the scene
    this will check if the 'breed_gene' or 'vaccine_gene' exists in the scene and delete them.
    """

    for nodeName in BAD_NODES:

        nodes = cmds.ls("*{}*".format(nodeName))
        for node in nodes:
            if cmds.objExists(node):
                cmds.delete(node)
                print("removed virus node: {}".format(node))