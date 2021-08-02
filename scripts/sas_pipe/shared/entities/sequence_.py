import os

import sas_pipe.shared.entities.abstract_entity_ as abstract_entity
import sas_pipe.shared.os_utils as dir


class Sequence(abstract_entity.AbstractEntity):
    def __init__(self, path):
        super(Sequence, self).__init__(path)

        if os.path.isdir(self.path):
            self.shots = sorted([f for f in dir.get_contents(self.path, dirs=True)])
        else:
            self.shots = list()
