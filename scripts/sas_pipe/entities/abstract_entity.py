"""This module contains the AbstractEntity class. The Entity class is for abstrace entities (ie. sequences)"""

import os
import getpass
import re
from time import gmtime, strftime
import json
from collections import OrderedDict

import sas_pipe.common as common
from sas_pipe import Logger
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.utils.data.abstract_data as abstract_data


class AbstractEntity(object):
    DEFAULT_DATA = OrderedDict()

    def __init__(self, path, name=None):
        """
        :param path: absoulte path of the entity
        """
        if pipeutils.checkTag(path, self.__class__.__name__):
            self.path = path

            if not name:
                self.name = os.path.basename(path)
            else:
                self.name = name
            self.name = re.sub("[^A-Za-z0-9_{}]", "", str(self.name))
            self.type = self.__class__.__name__

            self.manifest_path = os.path.join(self.path, '{}.manifest'.format(self.name))

            if os.path.exists(self.manifest_path):
                self.read()
            else:
                self.setData(self.DEFAULT_DATA)
        else:
            raise TypeError("{} is not of type {}".format(path, self.__class__.__name__))

    def __str__(self):
        description = \
            '''
            name: {name}
            type: {type}
            path: {path}
            '''

        return description.format(name=self.name, path=self.path, type=self.type)

    def read(self):
        data = abstract_data.AbstractData()
        data.read(self.manifest_path)
        self._data = data.getData()

    def setData(self, value):
        data = abstract_data.AbstractData()
        data.setData(value)
        self._data = data.getData()
        data.write(self.manifest_path)
