import os

from collections import OrderedDict
import sas_pipe.entities.element as element
import sas_pipe.utils.osutil as os_utils


def isShot(path):
    """
    Check is a path is an shot
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'shot')


class Shot(element.Element):
    DEFAULT_VARIANT = OrderedDict(
        [('anim', 'anim'), ('audio', 'audio'), ('comp', 'comp'), ('crowd', 'anim/crowd'), ('fx', 'fx'), ('lay', 'lay'),
         ('lght', 'lght'), ('sim', 'sim'), ('fin', 'fin')])

    DEFAULT_TASKS = DEFAULT_VARIANT.keys()

    DEFAULT_DATA = OrderedDict([('tasks', DEFAULT_TASKS), ('variants', {"base": DEFAULT_VARIANT})])

    def __init__(self, path):
        seq_type = os.path.basename(os_utils.get_parent(path, 2))
        seq = os.path.basename(os.path.dirname(path))
        shot = os.path.basename(path)
        self.name = '{}_{}_{}'.format(seq_type, seq, shot)

        super(Shot, self).__init__(path, name=self.name)


if __name__ == '__main__':
    sh = Shot(
        "/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio/shows/TEST/rel/sequences/seq/010/0010")
    print sh
