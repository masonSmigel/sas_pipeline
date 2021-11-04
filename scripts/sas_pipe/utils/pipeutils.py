"""

"""
import os
import sas_pipe.common as common
import sas_pipe.utils.osutil as osutil


def addEntityTag(path, type):
    """
    :param path:
    :param type:
    :return:
    """
    tag_file = path + "/.{}".format(type.lower())
    if type.lower() not in [x.lower() for x in common.DATATYPES]:
        raise ValueError('{} is not a valid tag.'.format(type))

    f = open(tag_file, "w")
    f.close()


def removeEntityTag(path, type):
    pass


def checkTag(path, tag):
    """
    Check if a path is a studio
    :param path: list the path
    :param tag: tag to check for
    :return:
    """
    if not os.path.exists(path):
        return False

    if '.{}'.format(tag.lower()) in osutil.get_contents(path, files=True, dirs=False):
        return True
    return False
