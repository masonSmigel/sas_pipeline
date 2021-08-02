import os

import sas_pipe.shared.entities.entity_ as entity


class Shot(entity.Entity):
    def __init__(self, path):
        super(Shot, self).__init__(path)

        self.name = '{}_{}'.format(os.path.basename(os.path.dirname(self.path)), os.path.basename(self.path))

