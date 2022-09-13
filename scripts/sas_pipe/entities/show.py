import os
from collections import OrderedDict

import sas_pipe.common as common
from sas_pipe import constants
import sas_pipe.constants
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.osutil as os_utils
from sas_pipe import environment
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.utils.data.abstract_data as abstract_data


def isShow(path):
    """
    Check if a path is a studio
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'show')


class Show(abstract_entity.AbstractEntity):
    """Studio class. Accepts the studio root as a parameter"""
    DEFAULT_DATA = OrderedDict(sequence_types=None,
                               element_types=None,
                               maya_file_type=sas_pipe.constants.MAYA_FILE_TYPE
                               )

    def __init__(self, path):
        super(Show, self).__init__(path)

        self.elementTypes = self._data['element_types']
        self.sequenceTypes = self._data['sequence_types']

    @staticmethod
    def create(path):
        """ Create a new show"""
        # add the proper tag
        pipeutils.addEntityTag(path, "show")

        show_entity = Show(path)

        # get the taks from the template defined in the json file
        elementTemplate = abstract_data.AbstractData()
        elementTemplate.read(constants.ELEMENT_TEMPLATE)
        elementTempalteData = elementTemplate.getData()
        elementTypes = list(elementTempalteData.keys())

        shotTemplate = abstract_data.AbstractData()
        shotTemplate.read(constants.SHOT_TEMPLATE)
        shotTemplateData = shotTemplate.getData()
        shotTypes = list(shotTemplateData.keys())

        # create the folders for elements and shots
        for type in elementTypes:
            os.makedirs(os.path.join(environment.getEnv('elm_path'), type))
        for type in shotTypes:
            os.makedirs(os.path.join(environment.getEnv('seq_path'), type))

        # create other important folders
        os.makedirs(os.path.join(environment.getEnv('pipe_path')))
        os.makedirs(os.path.join(environment.getEnv('develop_path')))
        os.makedirs(os.path.join(environment.getEnv('rnd_path')))
        os.makedirs(os.path.join(environment.getEnv('editorial_path')))
        os.makedirs(os.path.join(environment.getEnv('out_path')))

        show_entity.set_elementTypes(elementTypes)
        show_entity.set_sequenceTypes(shotTypes)

        return show_entity

    def set_elementTypes(self, values):
        data = self._data
        data['element_types'] = values
        self.setData(data)

    def set_sequenceTypes(self, values):
        data = self._data
        data['sequence_types'] = values
        self.setData(data)

    def get_elementTypes(self):
        return self._data['element_types']

    def get_sequenceTypes(self):
        return self._data['sequence_types']


if __name__ == "__main__":
    Show.create("test1")
