import os
from collections import OrderedDict

import sas_pipe.common as common
import sas_pipe.entities.abstract_entity as abstract_entity
import sas_pipe.utils.osutil as os_utils


class Show(abstract_entity.AbstractEntity):
    """Studio class. Accepts the studio root as a parameter"""
    DEFAULT_DATA = OrderedDict(shot_tasks=common.SHOT_TASKS,
                               sequence_types=common.SEQUENCE_TYPES,
                               asset_tasks=common.ASSET_TASKS,
                               asset_types=common.ASSET_TYPES,
                               maya_file_type=common.MAYA_FILE_TYPE
                               )

    def __init__(self, path):
        super(Show, self).__init__(path)

        self._initialize()

    def _initialize(self):
        """
        :return:
        """
        self.work_path = os.path.join(self.path, 'work')
        self.rel_path = os.path.join(self.path, 'rel')
        self.assets_path = os.path.join(self.work_path, 'assets')
        self.assets_path = os.path.join(self.work_path, 'sequences')

        os_utils.validate_directory(self.work_path, create=True)
        os_utils.validate_directory(self.rel_path, create=True)

        self.__tag_as_show()

    def gatherData(self):
        """
        Gather data about the entity
        :return:
        """
        pass

    def __tag_as_show(self):
        """Add a dot file to tag the root as a show"""
        f = open("{}/.is_SAS_show".format(self.path), "w")
        f.close()


if __name__ == '__main__':
    st = Show('/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/DEV_ROOT/shows/HEXL')
    print st
