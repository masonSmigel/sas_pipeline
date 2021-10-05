import os
from collections import OrderedDict

import sas_pipe.common as common
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.osutil as os_utils


def isStudio(path):
    if os.path.exists(path):
        if os.path.isfile(path + '/.isSasRoot'):
            return True
    return False


class Studio(abstract_entity.AbstractEntity):
    """Studio class. Accepts the studio root as a parameter"""
    DEFAULT_DATA = OrderedDict(depts=common.DEPTS, shows=[])

    def __init__(self, path):
        super(Studio, self).__init__(path)

        self._initialize()

    def update(self):
        """
        Check the manifest file for updates
        :return:
        """
        pass


if __name__ == '__main__':
    st = Studio('/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/DEV_ROOT')
    print st
