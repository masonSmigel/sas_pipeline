"""This module contains the entity_ class. The Entity class is for entities with concrete deliverables (ie. files)"""

import os
import shutil
from collections import OrderedDict

import sas_pipe.shared.common as common
import sas_pipe.shared.os_utils as os_utils
import sas_pipe.shared.entities.abstract_entity_ as abstract_entity
import sas_pipe.shared.filenames as naming
import sas_pipe.shared.os_utils as dir
import sas_pipe.shared.data.entity_data as entity_data
from sas_pipe import Logger

class Entity(abstract_entity.AbstractEntity):
    base_data = dict()

    def __init__(self, path):
        super(Entity, self).__init__(path)

        self.variant = None
        self.task = None
        self.mode = 'rel'

        self.manifest_path = None
        self.manifest_data = None
        self.tasks = list()

        self.manifest_path = os.path.join(self.rel_path, '{}.json'.format(self.name))
        self.write_manifest()
        self.read_manifest()

        self._get_tasks()

    def set_variant(self, variant):
        if self.manifest_data.has_key(variant):
            self.variant = variant
            print('{} varaint set to: {}'.format(self.name, self.variant))

    def set_task(self, task):
        self.task = task
        print('{} varaint set to: {}'.format(self.name, self.task))

    def set_mode(self, mode ):
        if mode in ['work', 'rel']:
            self.mode = mode
            print('{} Mode set to: {}'.format(self.name, self.mode))

    def list_all_files(self):
        """Get all files associated with this entity"""
        result = list()
        result.extend(self.list_work_files())
        result.extend(self.list_rel_files())
        return sorted(result)

    def list_work_files(self, task=None):
        """
        Get all files in the work mode
        :param task: task to return files from. If not provided files for all tasks will be returned
        :type: str
        :return: all files related to the entity
        :rtype: list
        """
        result = list()
        if task:
            path = os.path.join(self.work_path, task)
            result.extend([f for f in dir.get_contents(path, files=True)])
        else:
            for task in self.tasks:
                path = os.path.join(self.work_path, task)
                result.extend([f for f in dir.get_contents(path, files=True)])
        return result

    def list_rel_files(self, task=None):
        """
        Get all files in the release mode
        :param task: task to return files from. If not provided files for all tasks will be returned
        :type: str
        :return: all files related to the entity
        :rtype: list """
        result = list()
        if task:
            path = os.path.join(self.rel_path, task)
            result.extend([f for f in dir.get_contents(path, files=True)])
        else:
            for task in self.tasks:
                path = os.path.join(self.rel_path, task)
                result.extend([f for f in dir.get_contents(path, files=True)])
        return result

    def write_manifest(self):
        if not os.path.exists(self.manifest_path):
            asset_data = entity_data.EntityData()
            data = asset_data.getData()
            data['base'] = self.base_data
            asset_data.setData(data)
            asset_data.write(self.manifest_path)
            # Create a symbolic link so the file displays in both work and rel directories. The source is stored in rel.
            os.symlink(self.manifest_path, self.manifest_path.replace('rel', 'work'), )

    def read_manifest(self):
        asset_data = entity_data.EntityData()
        data = asset_data.read(self.manifest_path)
        self.manifest_data = data
        return self.manifest_data

    def _get_variants(self):
        data = entity_data.EntityData()
        data.read(self.manifest_path)
        variants_list = list()
        for variant in data.getData().keys():
            variants_list.append(variant)
        return variants_list

    def _get_tasks(self):
        self.tasks = list()
        for key in self.manifest_data['base'].keys():
            if key != 'variant':
                self.tasks.append(key)
        return sorted(self.tasks)

    def _get_file_from_directory(self, path, file_type=None):
        """
        get the newest version or publish file from a directory
        :param path:
        :param file_type:
        :return:
        """
        if naming.get_highest_index(path) > 0:
            return naming.get_highest_file(path)
        else:
            # Then the file is a publish file. Try to find the correct file
            for file in os_utils.get_contents(path=path, files=True):
                # If the name and task or name and variant are in the filename, return the file.
                if self.name in file and self.task in file or self.name in self.variant in file:
                    return file
                else:
                    Logger.error('No publish file found. Ensure file follows')
                    return None


if __name__ == '__main__':
    e = Entity('/Users/masonsmigel/Dropbox (Neko Productions)/SAS/shows/DEMO/work/assets/char/mrCube')
    e.task = 'mod'
    print e._get_file_from_directory(
        '/Users/masonsmigel/Dropbox (Neko Productions)/SAS/shows/DEMO/rel/assets/char/mrCube/mod', True)
