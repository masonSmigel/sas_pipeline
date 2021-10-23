import os
from collections import OrderedDict

import sas_pipe.utils.data.abstract_data as abstract_data
import sas_pipe.utils.osutil as os_util


class StudioData(abstract_data.AbstractData):

    def __init__(self):
        """
        constructor for the curve data class
        """
        super(StudioData, self).__init__()

    def gatherData(self, item):
        """
        gather some data about the studio. This includes shows, and departments.
        :param item: root path of the studio
        :return:
        """
        depts = list()
        shows = list()
        depts_path = os.path.join(item, )
        shows_path = os.path.join(item, 'shows')

        for dept in os_util.get_contents(depts_path, files=False, dirs=True):
            depts.append(dept)
        self._data.update(OrderedDict(path=item, depts_path = depts_path, depts=depts, shows=shows))

    def applyData(self):
        """
        Apply the data in the file
        :return:
        """
        self._data


if __name__ == '__main__':
    a = EntityData()
    a.add_variant('damage', 'data')
    print a.getData()
