import os
import getpass
from collections import OrderedDict

from sas_pipe import constants
from sas_pipe import path
import sas_pipe.utils.osutil as os_utils
import sas_pipe.utils.pipeutils as pipeutils
from sas_pipe import environment
import sas_pipe.common as common
import sas_pipe.entities.abstract_entity as abstract_entity
from sas_pipe.utils.data import abstract_data


def isElement(path):
    """
    Check is a path is an elm
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'element')


class Element(abstract_entity.AbstractEntity):
    FILENAME_SYNTAX = "{name}_{task}_{variant}_v{version}_{intials}"

    def __init__(self, path, name=None):
        super(Element, self).__init__(path, name)

    def __str__(self):
        description = '''
        name: {name}
        type: {type}
        path: {path}
        '''

        return description.format(name=self.name, path=self.path, type=self.type)

    def set_tasks(self, values):
        data = self._data
        data['tasks'] = values
        self.setData(data)

    def get_tasks(self):
        return list(self._data['variants']['base'].keys())

    @staticmethod
    def create(path, elementType):
        """
        Create a new element based on the type and name provided
        :param path: path to the element
        :param elementType: type of element to create. Valid values are set in the Element Template
        :return:
        """
        pipeutils.addEntityTag(path, 'element')

        element_entity = Element(path)

        elementTemplate = abstract_data.AbstractData()
        elementTemplate.read(constants.ELEMENT_TEMPLATE)
        elementTempalteData = elementTemplate.getData()

        if elementType not in elementTempalteData.keys():
            raise Exception("No element type: {} specified in template".format(elementType))

        data = OrderedDict()
        variantDict = OrderedDict()
        baseDict = OrderedDict()
        for task in elementTempalteData[elementType]:
            os.makedirs(os.path.join(path, task, constants.WORK_TOKEN))
            os.makedirs(os.path.join(path, task, constants.REL_TOKEN))
            os.makedirs(os.path.join(path, task, constants.VER_TOKEN))
            baseDict[task] = task

        variantDict['base'] = baseDict
        data['variants'] = variantDict

        element_entity.setData(data)

        return element_entity

    def composePath(self):
        """

        :return:
        """

    def add_task(self, taskName, path=None):
        """
        Add a new task
        :param taskName: new task
        :param path: path to task files
        :return:
        """
        data = self._data
        if taskName not in self.get_tasks():
            if path:
                os.makedirs(os.path.join(self.path, path, constants.WORK_TOKEN))
                os.makedirs(os.path.join(self.path, path, constants.REL_TOKEN))
                os.makedirs(os.path.join(self.path, path, constants.VER_TOKEN))
            else:
                os.makedirs(os.path.join(self.path, taskName, constants.WORK_TOKEN))
                os.makedirs(os.path.join(self.path, taskName, constants.REL_TOKEN))
                os.makedirs(os.path.join(self.path, taskName, constants.VER_TOKEN))

            self.setData(data)
        else:
            raise ValueError('Task "{}" already exists on asset "{}"'.format(taskName, self.name))
        return taskName

    def get_file_name(self, task, variant=None, work=True):
        """
        generate a filename
        :param task:
        :param variant:
        :param work:
        :return:
        """
        user = getpass.getuser()
        variant = variant or 'base'
        filename = self.FILENAME_SYNTAX.format(name=self.name, task=task, variant=variant, intials=user)
        return filename

    def compose_path(self, task, step, variant=None, fileName=None):
        """
        compose the file path
        :return:
        """
        if not variant: variant = 'base'
        if not fileName:
            return os.path.join(self.path, self.validate_variant_data(variant, task), step)
        else:
            return os.path.join(self.path, self.validate_variant_data(variant, task), step, fileName)

    def get_work_files(self, task, variant=None):
        """
        return a list of all the work files
        :param variant: Optional - specify a variant to get the files for. Otherwise just get the 'base'
        :param task: Optional - task to get files for. Otherwise get all tasks.
        :return:
        """
        if not variant: variant = 'base'
        path = self.compose_path(task, step=constants.WORK_TOKEN, variant=variant)
        return os_utils.get_contents(path, files=True, dirs=False)

    def get_publish_files(self, task, variant=None):
        """
        return a list of all the work files
        :param variant: Optional - specify a variant to get the files for. Otherwise just get the 'base'
        :param task: Optional - task to get files for. Otherwise get all tasks.
        :return:
        """
        if not variant: variant = 'base'
        path = self.compose_path(task, step=constants.REL_TOKEN, variant=variant)
        return os_utils.get_contents(path, files=True, dirs=False)

    def get_publish_version_files(self, task, variant=None):
        """

        :param task:
        :param variant:
        :return:
        """
        if not variant: variant = 'base'
        path = self.compose_path(task, step=constants.VER_TOKEN, variant=variant)
        return os_utils.get_contents(path, files=True, dirs=False)

    def get_thumbnail_path(self):
        thumbNailPath = os.path.join(self.path, 'thumbnail_{}.jpg'.format(self.name))
        return thumbNailPath

    def update_tasks(self):
        """
        Add any missing tasks from the element.json file
        """
        elementTemplate = abstract_data.AbstractData()
        elementTemplate.read(constants.ELEMENT_TEMPLATE)
        elementTempalteData = elementTemplate.getData()

        # determine the entiy type
        for type in elementTempalteData.keys():
            cleanPath = path.clean_path(self.path)
            if type in cleanPath:
                elementType = type
        print "type is", type
        print "found type is", elementType


        task_data = elementTempalteData[elementType]
        existing_tasks = os.listdir(self.path)
        for task in task_data:
            if task not in existing_tasks:
                self.add_task(taskName=task)
                print "adding new task {}/{}".format(self.path, task)

    # def add_variant(self, variant, **kwargs):
    #     """
    #     Setup a new variant and its data.
    #     :param variant: name of the variant
    #     :param kwargs: tasks to set the variant tasks to. (ex: mod = 'mod', tex = 'look/tex')
    #     :return:
    #     """
    #     data = self._data
    #
    #     var_data = OrderedDict()
    #     for kwarg in kwargs:
    #         if kwarg in self.get_tasks():
    #             var_data[kwarg] = kwargs[kwarg]
    #         else:
    #             raise ValueError('keyword "{}" is not a task for the Element "{}"'.format(kwarg, self.name))
    #
    #     if not data.has_key('variants'):
    #         data['variants'] = OrderedDict()
    #     data['variants'][variant] = var_data
    #     self.setData(data)

    # def set_variant(self, values):
    #     data = self._data
    #     data['variants'] = values
    #     self.setData(data)
    #
    # def get_variant_tasks(self, variant=None):
    #     if not variant: variant = 'base'
    #     return self._data['variants'][variant]
    #
    # def get_all_variants(self):
    #     return self._data['variants']

    def validate_variant_data(self, variant, task):
        """
        Get the data from a given variant and task.
        This is important when reading the variants so if there is no override we can get a path from the base
        :param variant: variant to read
        :param task: task to read
        :return: path to the data of a cariant, relative to asset
        """
        if not task:
            return None

        if self._data['variants'].has_key(variant):
            if self._data['variants'][variant].has_key(task):
                return self._data['variants'][variant][task]
        return self._data['variants']['base'][task]


if __name__ == '__main__':
    e = Element('/Users/masonsmigel/Documents/sastld2023/shows/TLD/elements/char/paladin')
    print e.get_tasks()

    e.update_tasks()
