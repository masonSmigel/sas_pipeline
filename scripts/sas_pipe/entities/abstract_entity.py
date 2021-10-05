"""This module contains the AbstractEntity class. The Entity class is for abstrace entities (ie. sequences)"""

import os
import getpass
from time import gmtime, strftime
import json
from collections import OrderedDict

import sas_pipe.common as common
from sas_pipe import Logger


class AbstractEntity(object):
    DEFAULT_DATA = OrderedDict()

    def __init__(self, path):
        """
        :param path: absoulte path of the entity
        """

        self.path = path
        self.name = os.path.basename(path)
        self.type = self.__class__.__name__

        self.manifest_path = os.path.join(self.path, '{}.json'.format(self.name))

        if os.path.exists(self.manifest_path):
            self.read()
        else:
            self._data = self.DEFAULT_DATA

        self._initialize()

        self.gatherData()
        self.write()

    def __str__(self):
        description = \
            '''
            name: {name}
            type: {type}
            path: {path}
            '''

        return description.format(name=self.name, path=self.path, type=self.type)

    def _initialize(self):
        """overwrite in subclasses to setup the nessesary files"""
        pass
