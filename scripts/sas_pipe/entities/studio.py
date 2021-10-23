import os
from collections import OrderedDict

import sas_pipe.common as common
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.osutil as os_utils
import sas_pipe.utils.pipeutils as pipeutils


# Studio functions
def isstudio(path):
    """
    Check if a path is a studio
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'studio')


class Studio(abstract_entity.AbstractEntity):
    """Studio class. Accepts the studio root as a parameter"""
    DEFAULT_DATA = OrderedDict(depts=common.DEPTS, shows=[])

    def __init__(self, path):
        super(Studio, self).__init__(path)

    def update(self):
        """
        Check the manifest file for updates
        :return:
        """
        pass

    def add_dept(self, dept):
        data = self._data
        data['depts'] = self._data['depts'] + [dept]
        self.setData(data)

    def add_show(self, show):
        data = self._data
        data['shows'] = self._data['shows'] + [show]
        self.setData(data)

    def rm_dept(self, dept):
        data = self._data
        data['depts'].remove(dept)
        self.setData(data)

    def rm_show(self, show):
        data = self._data
        data['shows'].remove(show)
        self.setData(data)


if __name__ == '__main__':
    st = Studio('/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/DEV_ROOT')
    print st
