"""This module contains the entity_ class. The Entity class is for entities with concrete deliverables (ie. files)"""

import os

import sas_pipe.shared.common as common
import sas_pipe.shared.entities.abstract_entity_ as abstract_entity
import sas_pipe.shared.naming as naming
import sas_pipe.shared.os_utils as dir
from sas_pipe.shared.logger import Logger


class Entity(abstract_entity.AbstractEntity):

    def __init__(self, path):
        super(Entity, self).__init__(path)

        if os.path.isdir(self.path):
            self.tasks = sorted([f for f in dir.get_contents(self.path, dirs=True)])
        else:
            self.tasks = list()

    def get_newest_version(self, task, return_path=False):
        """
        Get the file with the highest index from a specified task. Always returns file in the working path
        :param task: task to get version from
        :param return_path: return the full path of the file
        :return: highest version in the task
        """
        if self.validate_task(task):
            task_path = os.path.join(self.work_path, task)
            if naming.get_highest_index(task_path, return_file=True):
                if return_path:
                    return os.path.join(task_path, naming.get_highest_index(task_path, return_file=True))

                return naming.get_highest_index(task_path, return_file=True)

            return None

    def get_publish(self, task, file_type=None):
        """
       get the publish file if one exists
       :param task: task to get file from
       :param file_type: Optional- if several files with the same predicted base name exist the filetype is used to get the
                         correct file. Otherwise the first file alphabetically will be selected.
       :return: published file for the specified task
       """
        if self.validate_task(task):
            task_path = os.path.join(self.rel_path, task)
            guess_base_name = '{}_{}'.format(self.name, task)
            if file_type:
                file_name = '{}.{}'.format(guess_base_name, file_type)
                if os.path.isfile(os.path.join(task_path, file_name)):
                    return file_name
            else:
                safety_list = list()
                for file in [f for f in dir.get_contents(task_path, files=True)]:
                    if guess_base_name in file:
                        safety_list.append(file)
                if len(safety_list) > 1:
                    Logger.warning(
                        'Several publish files found. Please specify a file type or delete/rename invalid files.')
                return common.getFirstIndex(safety_list)

    def get_all_files(self):
        """Get all files associated with this entity"""
        result = list()
        result.extend(self.get_work_files())
        result.extend(self.get_rel_files())
        return sorted(result)

    def get_work_files(self, task=None):
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

    def get_rel_files(self, task=None):
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

    def validate_task(self, task):
        if self.tasks:
            if task in self.tasks:
                return True
        else:
            Logger.error('{} is not a valid task. Valid tasks are: {}'.format(task, self.tasks))
        return False
