# coding=utf-8
"""
This module contains functions common to all modules and constants
"""
from collections import OrderedDict

# Path Constants
current_path = __file__.replace('\\', '/')

# Maya module paths
ICONS_PATH = '/'.join(current_path.split('/')[0:-4]) + '/icons'
PLUGIN_PATH = '/'.join(current_path.split('/')[0:-4]) + '/plug-ins'
SCRIPTS_PATH = '/'.join(current_path.split('/')[0:-4]) + '/scripts'

# path constants.
# Paths are relative to the root of the project.
SHOWS_PATH = 'shows'
DEPTS_PATH = 'depts'

CURRENTSHOW_PATH = SHOWS_PATH + '/{currentShow}'

REL_PATH = CURRENTSHOW_PATH + '/rel'
WORK_PATH = CURRENTSHOW_PATH + '/work'

ASSET_WORK_PATH = WORK_PATH + "/assets"
SEQ_WORK_PATH = WORK_PATH + "/sequences"
ASSET_REL_PATH = REL_PATH + "/assets"
SEQ_REL_PATH = REL_PATH + "/sequences"

ESSENTIAL_PATHS = [SHOWS_PATH, DEPTS_PATH, CURRENTSHOW_PATH, REL_PATH, WORK_PATH, ASSET_WORK_PATH, SEQ_WORK_PATH,
                   ASSET_REL_PATH, SEQ_REL_PATH]

# Project Defaults
ASSET_TYPES = ['char', 'prop', 'set', 'setPeice']  # Asset types
SEQUENCE_TYPES = ['pub', 'seq']  # sequence type
ASSET_TASKS = ['mod', 'rig', 'look', 'conc']  # Asset Departments
SHOT_TASKS = ['audio', 'lay', 'anim', 'crowd', 'fx', 'sim', 'lgt', 'comp']  # Shot Departments
OTHER_DEPTS = ['core']  # Other Departments

DEPTS = ASSET_TASKS + SHOT_TASKS + OTHER_DEPTS

SEQ_PADDING = 2
SHOT_PADDING = 3

# File type constants
MAYA_FILE_TYPE = 'ma'

DATATYPES = ['StudioData', 'ShowData', 'SeqData', 'ShotData', 'AssetData']


def toList(values):
    """
    Converts values into a items
    :param values: values to convert into a items
    :return: items of values
    """
    if not isinstance(values, (list, tuple)):
        values = [values]
    return values


def getFirstIndex(var):
    """
    Return the first index of a items
    :param var: items to get index from
    :type var: list | tuple
    :return: first index of a items or tuple
    """
    if isinstance(var, (list, tuple)):
        if not len(var):
            return var
        return var[0]
    else:
        return var


def convertDictKeys(dictionary):
    """
    Converts Dictionary keys from unicodes to strings

    :param dictionary: the ditionary you want to convert the eyes on
    :type dictionary: dict

    :return: The dictionary with its keys converted
    :rtype: dict
    """

    # If its not a dictionary return it.
    if not isinstance(dictionary, dict):
        return dictionary

    # If its a dictionary look through the keys/values and convert them
    return OrderedDict((str(k), convertDictKeys(v)) for k, v in dictionary.items())


def tryIndex(list, index):
    try:
        return list[index]
    except IndexError:
        return None
