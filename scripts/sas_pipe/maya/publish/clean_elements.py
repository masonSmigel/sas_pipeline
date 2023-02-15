""" This module contains publish steps for all element files"""

import os 
import maya.cmds as cmds
import maya.mel as mel


# --------------------------------------------------------------------------------
# Clean scene functions from rigamajig2
# --------------------------------------------------------------------------------
def cleanNodes():
    """
    Clean up unused nodes.
    Remove all nodes that are not connected to anything.
    """
    # source the new MLdeleteUnused to solve a bug deleting the default aiStandard shader in Maya2020
    ovMLdeleteUnusedPath = '/'.join(__file__.split(os.sep)[:-1]) + '/MLdeleteUnused.mel'
    mel.eval('source "{}"'.format(ovMLdeleteUnusedPath))

    mel.eval("MLdeleteUnused")
    nodes = cmds.ls(typ=['groupId', 'nodeGraphEditorInfo', 'nodeGraphEditorBookmarkInfo', 'unknown'])
    if nodes:
        for node in nodes:
            nodeType = cmds.nodeType(node)
            isConnected = cmds.listHistory(node, f=True, il=True)
            if ("GraphEditor" in nodeType) or ("unknown" in nodeType) or not isConnected:
                try:
                    cmds.lockNode(node, l=False)
                    cmds.delete('node')
                    print("Cleaned Node: '{}'".format(node))
                except:
                    pass


def cleanPlugins():
    """
    Clean unknown plugins.
    Remove unkown plugins in the scene
    """
    plugins = cmds.unknownPlugin(q=True, l=True)
    if plugins:
        for plugin in plugins:
            try:
                cmds.unknownPlugin(plugin, r=True)
                print("Cleaned Plugin: '{}'".format(plugin))
            except:
                pass


def cleanScriptNodes(excludedScriptNodes=list(), excludePrefix='rigamajig2'):
    """
    Clean all scriptnodes in the scene.
    By default script nodes with the prefix 'rigamajig2' will be ignored
    :param excludedScriptNodes: list of script nodes to be kept
    :param excludePrefix: prefix used to filter script nodes. All nodes with the prefix are kept.
    """
    all_script_nodes = cmds.ls(type='script')
    for script_node in all_script_nodes:
        if script_node.startswith(excludePrefix):
            continue
        if script_node in excludedScriptNodes:
            continue

        cmds.delete(script_node)
        print("Cleaned Script Node: '{}'".format(script_node))


def cleanRougePanels(panels=list()):
    """
    cleanup rouge procedures from all modelPanels
    It will remove errors like:
        // Error: line 1: Cannot find procedure "CgAbBlastPanelOptChangeCallback". //
        // Error: line 1: Cannot find procedure "DCF_updateViewportList". //
    """
    if not isinstance(panels, (list, tuple)):
        panels = [panels]
    EVIL_METHOD_NAMES = ['DCF_updateViewportList', 'CgAbBlastPanelOptChangeCallback', 'onModelChange3dc'] + panels
    capitalEvilMethodNames = [name.upper() for name in EVIL_METHOD_NAMES]
    modelPanelLabel = mel.eval('localizedPanelLabel("ModelPanel")')
    processedPanelNames = []
    panelName = cmds.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
    while panelName and panelName not in processedPanelNames:
        editorChangedValue = cmds.modelEditor(panelName, query=True, editorChanged=True)
        parts = editorChangedValue.split(';')
        newParts = []
        changed = False
        for part in parts:
            for evilMethodName in capitalEvilMethodNames:
                if evilMethodName in part.upper():
                    changed = True
                    print("removed callback '{}' from pannel '{}'".format(part, panelName))
                    break
            else:
                newParts.append(part)
        if changed:
            cmds.modelEditor(panelName, edit=True, editorChanged=';'.join(newParts))
        processedPanelNames.append(panelName)
        panelName = cmds.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel)) or None


# --------------------------------------------------------------------------------
# Functions for asset files
# --------------------------------------------------------------------------------
def cleanNamespaces():
    """
    Delete all namespaces from a scene
    """
    toExclude = ('UI', 'shared')
    ns_dict = {}
    for ns_find in (x for x in cmds.namespaceInfo(':', listOnlyNamespaces=True, recurse=True, fn=True) if
                    x not in toExclude):
        ns_dict.setdefault(len(ns_find.split(":")), []).append(ns_find)

    for i, lvl in enumerate(reversed(ns_dict.keys())):
        for namespace in ns_dict[lvl]:
            cmds.namespace(removeNamespace=namespace, mergeNamespaceWithParent=True)
            print ("removed namespace {}".format(namespace))


def importReferences():
    """
    Import all References in the file
    """
    refs = cmds.ls(type='reference')

    for ref in refs:
        rFile = cmds.referenceQuery(ref, f=True)
        try:
            cmds.file(rFile, importReference=True)
            print("imported reference: {}".format(rFile))
        except:
            print("Failed to import reference node for: {}".format(rFile))
