"""
Get and set some enviornment variables
"""

import os
from collections import OrderedDict

VAR_PREFIX = 'SAS_'


def setEnv(variable, value):
    """
    Set the
    :param variable:
    :param value:
    :return:
    """
    os.environ[VAR_PREFIX + variable.upper()] = value


def getEnv(varible):
    """
    :param varible:
    :return:
    """
    res = os.environ.get(VAR_PREFIX + varible.upper())
    return res


def getAll():
    """
    :return:
    """
    res = dict()
    for key, val in os.environ.iteritems():
        if key.startswith(VAR_PREFIX):
            res[key] = val
    return res


def flushEnv():

    environ_varibles = os.environ.copy()
    print environ_varibles
    for key, val in environ_varibles.iteritems():
        if key.startswith(VAR_PREFIX):
            del os.environ[key]


if __name__ == '__main__':
    setEnv('Root', '/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root')
    setEnv('user', 'me')
    setEnv('currentShow', 'HOWB')

    print getAll()
