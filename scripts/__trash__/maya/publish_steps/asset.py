"""Publish functions for Assets"""
import pymel.core as pm 


def remove_all_namespaces():
    """
    Remove all namespaces
    """
    toExclude = ('UI', 'utils')
    ns_dict = {}
    for ns_find in (x for x in pm.namespaceInfo(':', listOnlyNamespaces=True, recurse=True, fn=True)
        if not x in toExclude):
        ns_dict.setdefault(len(ns_find.split(":")), []).append(ns_find)
    i=0
    for lvl in reversed(ns_dict.keys()):
        for this_ns in ns_dict[lvl]:
            pm.namespace(removeNamespace=this_ns, mergeNamespaceWithParent=True)
            i=i+1


def import_all_references():
    """
    Import all References in the file
    """
    refs = pm.listReferences()
    
    for ref in refs:
        ref.importContents()


def delete_unused_nodes():
    """
    Delete unused nodes
    """
    print "delete unused nodes"

