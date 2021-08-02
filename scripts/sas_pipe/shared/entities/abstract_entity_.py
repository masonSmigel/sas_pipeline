"""This module contains the AbstractEntity class. The Entity class is for abstrace entities (ie. sequences)"""

import os

import sas_pipe.shared.common as common
import sas_pipe.shared.os_utils as dir
from sas_pipe.shared.logger import Logger


class AbstractEntity(object):
    def __init__(self, path):
        """
        :param path: absoulte path of the entity
        """
        self.path = path
        self.name = os.path.basename(path)
        self.type = self.__class__.__name__

        if os.path.isdir(self.path):
            self._get_work_rel_paths()
        else:
            Logger.error('entity at {} is not valid.'.format(self.path))
            self.rel_path = None
            self.work_path = None

    def __str__(self):
        description = '''
        name: {name}
        type: {type}
        path: {path}
        '''
        return description.format(name=self.name, path=self.path, type=self.type)

    def _get_work_rel_paths(self):
        if common.WORK in self.path:
            self.work_path = self.path
            self.rel_path = str(self.path).replace(common.WORK, common.REL)
        elif common.REL in self.path:
            self.rel_path = self.path
            self.work_path = str(self.path).replace(common.REL, common.WORK)
        else:
            Logger.warning('failed to generate work and release paths for {}'.format(self.path))
            return False

    def _get_tasks(self):
        self.tasks = sorted([f for f in dir.get_contents(self.path, dirs=True)])
        return self.tasks

