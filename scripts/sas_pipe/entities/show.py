import os
from collections import OrderedDict

import sas_pipe.common as common
import sas_pipe.constants
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.osutil as os_utils
import sas_pipe.utils.pipeutils as pipeutils


def isShow(path):
    """
    Check if a path is a studio
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'show')


class Show(abstract_entity.AbstractEntity):
    """Studio class. Accepts the studio root as a parameter"""
    DEFAULT_DATA = OrderedDict(sequence_types=sas_pipe.constants.SEQUENCE_TYPES,
                               element_types=sas_pipe.constants.ASSET_TYPES,
                               maya_file_type=sas_pipe.constants.MAYA_FILE_TYPE
                               )

    def __init__(self, path):
        super(Show, self).__init__(path)
        self.elementTypes = self._data['element_types']
        self.sequenceTypes = self._data['sequence_types']

    def set_assetTypes(self, values):
        data = self._data
        data['element_types'] = values
        self.setData(data)

    def set_sequenceTypes(self, values):
        data = self._data
        data['sequence_types'] = values
        self.setData(data)

    def get_assetTypes(self):
        return self._data['element_types']

    def get_sequenceTypes(self):
        return self._data['sequence_types']

