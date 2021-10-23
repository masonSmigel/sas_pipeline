import sas_pipe.entities.entity as entity
import os
from collections import OrderedDict
import sas_pipe.utils.osutil as os_utils
import sas_pipe.utils.pipeutils as pipeutils


def isElement(path):
    """
    Check is a path is an element
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'element')


class Element(entity.Entity):
    DEFAULT_VARIANT = OrderedDict(
        [('conc', 'conc'), ('mod', 'mod'), ('rig', 'rig'), ('tex', 'look/tex'), ('mat', 'look/mat')])

    DEFAULT_TASKS = DEFAULT_VARIANT.keys()

    DEFAULT_DATA = OrderedDict([('tasks', DEFAULT_TASKS), ('variants', {"base": DEFAULT_VARIANT})])

    def __init__(self, path, name=None):
        super(Element, self).__init__(path, name)
        self.work_path = self.path.replace('/rel/', '/work/', )
        self.rel_path = self.path.replace('/work/', '/rel/')

    def __str__(self):
        description = \
            '''
            name: {name}
            type: {type}
            work_path: {work_path}
            rel_path: {rel_path}
            '''

        return description.format(name=self.name, work_path=self.work_path, rel_path=self.rel_path, type=self.type)

    def add_variant(self, variant, **kwargs):
        """
        Setup a new variant and its data.
        :param variant: name of the variant
        :param kwargs: tasks to set the variant tasks to. (ex: mod = 'mod', tex = 'look/tex')
        :return:
        """
        data = self._data

        var_data = OrderedDict()
        for kwarg in kwargs:
            if kwarg in self.get_tasks():
                var_data[kwarg] = kwargs[kwarg]
            else:
                raise ValueError('keyword "{}" is not a task for the Element "{}"'.format(kwarg, self.name))

        if not data.has_key('variants'):
            data['variants'] = OrderedDict()
        data['variants'][variant] = var_data
        self.setData(data)

    def set_variant(self, values):
        data = self._data
        data['variants'] = values
        self.setData(data)

    def get_variant_tasks(self, variant=None):
        if not variant: variant = 'base'
        return self._data['variants'][variant]

    def get_all_variants(self):
        return self._data['variants']

    def get_work_files(self, task, variant=None):
        """
        return a list of all the work files
        :param variant: Optional - specify a variant to get the files for. Otherwise just get the 'base'
        :param task: Optional - task to get files for. Otherwise get all tasks.
        :return:
        """
        if not variant: variant = 'base'

        path = os.path.join(self.work_path, self.validate_variant_data(variant, task))
        return os_utils.get_contents(path, files=True, dirs=False)

    def get_rel_files(self, task, variant=None):
        """
        return a list of all the work files
        :param variant: Optional - specify a variant to get the files for. Otherwise just get the 'base'
        :param task: Optional - task to get files for. Otherwise get all tasks.
        :return:
        """
        if not variant: variant = 'base'
        path = os.path.join(self.rel_path, self.validate_variant_data(variant, task))
        return os_utils.get_contents(path, files=True, dirs=False)

    def validate_variant_data(self, variant, task):
        """
        Get the data from a given variant and task.
        This is important when reading the variants so if there is no override we can get a path from the base
        :param variant: variant to read
        :param task: task to read
        :return: path to the data of a cariant, relative to asset
        """
        if self._data['variants'].has_key(variant):
            if self._data['variants'][variant].has_key(task):
                return self._data['variants'][variant][task]
        return self._data['variants']['base'][task]


if __name__ == '__main__':
    e = Element(
        '/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio/shows/TEST/work/elements/char/testCharacter')
    e.get_tasks()
    e.add_task('bshp', 'rig/bshp')
    # e.add_task('bshp', 'rig/bshp')
    # e.add_variant('worn', rig='rig/wear')
    # e.add_task('bshps', 'rig/bshps')
    # e.add_variant('worn', mod='mod/worn')
    # print e.get_all_variants()
