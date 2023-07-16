import os

from collections import OrderedDict

from sas_pipe import constants
from sas_pipe import path
import sas_pipe.common as common
import sas_pipe.entities.element as elm
import sas_pipe.utils.osutil as osutil
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.environment as environment
from sas_pipe.utils.data import abstract_data
from sas_pipe import Logger


def isShot(path):
    """
    Check is a path is an shot
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'shot')


class Shot(elm.Element):

    def __init__(self, path):
        seq_type = os.path.basename(osutil.get_parent(path, 2))
        seq = os.path.basename(os.path.dirname(path))
        shot = os.path.basename(path)
        self.name = '{}_{}_{}'.format(seq_type, seq, shot)

        super(Shot, self).__init__(path, name=self.name)

    @staticmethod
    def create(path, shotType):
        """
        Create a new element based on the type and name provided
        :param path: path to the element
        :param shotType: type of element to create. Valid values are set in the Element Template
        :return:
        """
        pipeutils.addEntityTag(path, 'shot')

        shot_entity = Shot(path)

        shotTemplate = abstract_data.AbstractData()
        shotTemplate.read(constants.SHOT_TEMPLATE)
        shotTemplateData = shotTemplate.getData()

        if shotType not in shotTemplateData.keys():
            raise Exception("No Shot type: {} specified in template".format(shotType))

        data = OrderedDict()
        variantDict = OrderedDict()
        baseDict = OrderedDict()
        for task in shotTemplateData[shotType]:
            os.makedirs(os.path.join(path, task, constants.WORK_TOKEN))
            os.makedirs(os.path.join(path, task, constants.REL_TOKEN))
            os.makedirs(os.path.join(path, task, constants.VER_TOKEN))
            baseDict[task] = task

        variantDict['base'] = baseDict
        data['variants'] = variantDict
        data['elements'] = OrderedDict()

        shot_entity.setData(data)

        return shot_entity

    def add_element(self, element, type, task, variant=None, override=None):
        """
        Add an elm to the shot
        :param element: name of the element to add
        :param type: type of asset (ie. 'char', 'prop', 'set', 'setPeice')
        :param task: task step to add to the shot (ie. 'mod', 'rig', 'tex', 'mat')
        :param variant: Optional - specify a variant to use
        :param override: Optional - specifiy an override for the variant and task.
                        use a path relative to the
        :return:
        """
        if not variant: variant = 'base'
        element_data = OrderedDict(
            [('element', element), ('type', type), ('task', task), ('variant', variant), ('override', override)])
        data = self._data

        # check if an alement wit this name already exists
        if element in data['elements']:
            for i in range(2000):
                if element + str(i) not in data['elements']:
                    element = element + str(i)
                    break

        data['elements'][element] = element_data
        self.setData(data)

    def rm_element(self, element):
        """
        Remove an element from the shot
        :param element: name of the element to delete
        """
        data = self._data
        if element in data['elements']:
            del data['elements'][element]
            self.setData(data)
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(element))

    def get_elements(self):
        """
        Get all elements that are part of this shot
        :return:
        """
        return self._data['elements'].keys()

    def get_element_data(self, element):
        """
        Get the data of an element
        :param element:
        :return:
        """
        if element in self._data['elements']:
            return self._data['elements'][element]
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(element))

    def set_element(self, elementCode, task=None, variant=None, override=None):
        """
        Set the element data
        :param elementCode: element code (dictionary key) of the element to edit
        :param task: task step to add to the shot (ie. 'mod', 'rig', 'tex', 'mat')
        :param variant: Optional - specify a variant to use
        :param override: Optional - specifiy an override for the variant and task.
                        use a path relative to the
        :return:
        """
        data = self._data
        if elementCode in data['elements']:
            if task: data['elements'][elementCode]['task'] = task
            if variant: data['elements'][elementCode]['variant'] = variant
            if override: data['elements'][elementCode]['override'] = override
            self.setData(data)
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(elementCode))

    def update_tasks(self):
        """
        Add any missing tasks from the element.json file
        """
        shotTemplateData = abstract_data.AbstractData()
        shotTemplateData.read(constants.SHOT_TEMPLATE)
        shotTempalteData = shotTemplateData.getData()

        # determine the entiy type
        for type in shotTempalteData.keys():
            cleanPath = path.clean_path(self.path)
            if type in cleanPath:
                shotType = type

        task_data = shotTempalteData[shotType]
        existing_tasks = os.listdir(self.path)
        for task in task_data:
            if task not in existing_tasks:
                self.add_task(taskName=task)
                Logger.info("adding new task {}/{}".format(self.path, task))


if __name__ == '__main__':
    sh = Shot("/Users/masonsmigel/Documents/SAS_DEV/shows/TEST/sequences/seq/010/0010")
    # sh.add_task('new')

    print(sh.add_element('testCharacter', 'char', 'rig'))
    sh.get_element_data('testCharacter')
    sh.set_element('testCharacter', task='mod', override='rig/test.ma')
    #
    # elements = sh.get_elements()
    #
    # sh.rm_element('testCharacter')
