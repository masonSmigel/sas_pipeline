import os

from collections import OrderedDict
import sas_pipe.entities.entity as entity
import sas_pipe.utils.osutil as os_utils


class Shot(entity.Entity):
    base_data = OrderedDict({'variant': False,
                             'mod': 'mod',
                             'rig': 'rig',
                             'tex': 'look/tex',
                             'mat': 'look/mat',
                             })

    def __init__(self, path):
        super(Shot, self).__init__(path)

        seq_type = os.path.basename(os_utils.get_parent(self.path, 2))
        seq = os.path.basename(os.path.dirname(self.path))
        shot = os.path.basename(self.path)
        self.name = '{}_{}_{}'.format(seq_type, seq, shot)


if __name__ == '__main__':
    print Shot("/Users/masonsmigel/Dropbox (Neko Productions)/SAS/shows/DEMO/work/sequences/seq/010/0010")
