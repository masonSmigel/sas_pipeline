""" This module manages directories"""

import os

from sas_pipe.shared.logger import Logger

IGNORE_FILES = ['.DS_Store', '__init__.py']


def create_directory(directory):
    """
    :param directory: path to create
    :type directory: str

    :return: path. if creation failed return None
    :rtype: str
    """
    if not os.path.isdir(directory):
        Logger.debug('making path{0}'.format(directory))
        try:
            os.makedirs(directory)
        except:
            Logger.error("Failed to create path: {}".format(directory))
            return None
    return directory


def validate_directory(directory, create=False):
    """
    check if a path exists
    :param directory: path to validate
    :type directory: str

    :param create: create directories if they dont exist
    :type create: bool
    """
    if isinstance(directory, (list, tuple)):
        directory = directory[0]
    if not os.path.exists(directory):
        if create:
            os.makedirs(directory)
            return True
        else:
            return False
    else:
        return True


def validate_directories(directories, create=True):
    """
    Check if directories exist. if create is on, it will make the path
    :param directories: items of directories to validate
    :type directories: list

    :param create: create directories if they dont exist
    :type create: bool

    :return: paths. if creation failed return None
    :rtype: list
    """
    for directory in directories:
        validate_directory(directory, create=create)


def get_contents(path, dirs=False, files=False):
    """
    List all folder Contents
    :param path: path to get_contents
    :param dirs: get_contents only directories
    :param files: get_contents only files
    :return:
    """
    if dirs:
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    elif files:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f not in IGNORE_FILES]
    else:
        return [f for f in os.listdir(path) if f not in IGNORE_FILES]


def get_parent(path, steps):
    """
    get the parent above a foldder
    :param path: path to get from
    :param steps: number of steps above
    :type steps: int
    :return: parent path
    :rtype: str
    """
    parent_dir = '/'.join(path.split('/')[0: (-1 * steps)])
    return parent_dir


def locate(dir, paths_to_search, base_only=False):
    """
    Look through paths and locate a folder
    :param dir: folder to look for
    :type dir: str

    :param paths_to_search: paths to look in
    :type paths_to_search: list

    :param base_only: If True only the base path will be returned. False returns a full path
    :type base_only: bool

    :return: parent path of folder
    """

    for path in paths_to_search:
        if dir in os.listdir(path):
            if base_only:
                return os.path.basename(path)
            else:
                return path

    Logger.debug("Could not locate: {}".format(dir))
    return None
