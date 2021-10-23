"""This module contains the entity_ class. The Entity class is for entities with concrete deliverables (ie. files)"""

import os

import sas_pipe.common as common
import sas_pipe.utils.osutil as os_utils
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.filenames as naming
import sas_pipe.utils.osutil as dir
from sas_pipe import Logger


class Entity(abstract_entity.AbstractEntity):
    base_data = dict()

    def __init__(self, path, name=None):
        super(Entity, self).__init__(path, name)

    # COMMON TO ELEMENTS AND SHOTS
    def set_tasks(self, values):
        data = self._data
        data['tasks'] = values
        self.setData(data)

    def get_tasks(self):
        return self._data['tasks']

    def add_task(self, new, path=None):
        """
        Add a new task
        :param new: new task
        :param path: path to task files
        :return:
        """
        data = self._data
        if new not in data['tasks']:
            data['tasks'].append(new)
            if path:
                data['variants']['base'][new] = path
                os.makedirs(os.path.join(self.work_path, path))
                os.makedirs(os.path.join(self.rel_path, path))
            self.setData(data)
        else:
            raise ValueError('Task "{}" already exists on asset "{}"'.format(new, self.name))
        return new


if __name__ == '__main__':
    entity = Entity(
        '/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio/shows/TEST/work/asset/char/testCharacter')
    print entity
