""" This module contains publish steps for models"""
import pymel.core as pm


def delete_history():
    """ 
    Delete History on all geo objects. 
    Any geometry that will be rendered and or rigged must have the suffix 'geo'. 
    Only meshes with the suffix 'geo' will be cleaned
    """

    for geo in pm.ls("*_geo"):
        if geo.getShape().type() == 'mesh':
            pm.delete(geo, ch=True)


def freeze_transformations():
    """ 
    Freeze Transfroms on all geo objects. 
    Any geometry that will be rendered and or rigged must have the suffix 'geo'. 
    Only meshes with the suffix 'geo' will be cleaned
    """
    for geo in pm.ls("*_geo"):
        if geo.getShape().type() == 'mesh':
            pm.makeIdentity(geo, apply=True, t=True, r=True, s=True)


def delete_display_layers():
    """
    Delete all display layers
    """

    for layer in pm.ls(long=True, type='displayLayer'):
        pm.delete(layer)
