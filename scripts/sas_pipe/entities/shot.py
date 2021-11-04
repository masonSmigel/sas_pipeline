import os

from collections import OrderedDict
import sas_pipe.entities.element as elm
import sas_pipe.utils.osutil as osutil
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.environment as environment


def isShot(path):
    """
    Check is a path is an shot
    :param path:
    :return:
    """
    return pipeutils.checkTag(path, 'shot')


class Shot(elm.Element):
    DEFAULT_VARIANT = OrderedDict(
        [('anim', 'anim'), ('audio', 'audio'), ('comp', 'comp'), ('crowd', 'anim/crowd'), ('fx', 'fx'), ('lay', 'lay'),
         ('lght', 'lght'), ('sim', 'sim'), ('fin', 'fin')])

    DEFAULT_TASKS = DEFAULT_VARIANT.keys()

    DEFAULT_DATA = OrderedDict(
        [('tasks', DEFAULT_TASKS), ('variants', {"base": DEFAULT_VARIANT}), ('elements', OrderedDict())])

    def __init__(self, path):
        seq_type = os.path.basename(osutil.get_parent(path, 2))
        seq = os.path.basename(os.path.dirname(path))
        shot = os.path.basename(path)
        self.name = '{}_{}_{}'.format(seq_type, seq, shot)

        super(Shot, self).__init__(path, name=self.name)

    def add_element(self, element, type, task, variant=None, override=None):
        """
        Add an elm to the shot
        :param element: name of the element to add
        :param type: type of asset (ie. 'char', 'prop', 'set', 'setPeice')
        :param task: task step to add to the shot (ie. 'mod', 'rig', 'tex', 'mat')
        :param variant: Optional - specify a variant to use
        :param override: Optional - specifiy an override for the variant and task.
                        use a path relative to the
        :return:
        """
        if not variant: variant = 'base'
        element_data = OrderedDict(
            [('element', element), ('type', type), ('task', task), ('variant', variant), ('override', override)])
        data = self._data

        # check if an alement wit this name already exists
        if data['elements'].has_key(element):
            for i in range(2000):
                if not data['elements'].has_key(element + str(i)):
                    element = element + str(i)
                    break

        data['elements'][element] = element_data
        self.setData(data)

    def rm_element(self, element):
        """
        Remove an element from the shot
        :param element: name of the element to delete
        """
        data = self._data
        if data['elements'].has_key(element):
            print 'remove element'
            del data['elements'][element]
            self.setData(data)
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(element))

    def get_elements(self):
        """
        Get all elements that are part of this shot
        :return:
        """
        return self._data['elements'].keys()

    def get_element_data(self, element):
        """
        Get the data of an element
        :param element:
        :return:
        """
        if self._data['elements'].has_key(element):
            return self._data['elements'][element]
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(element))

    def set_element(self, elementCode, task=None, variant=None, override=None):
        """
        Set the element data
        :param elementCode: element code (dictionary key) of the element to edit
        :param task: task step to add to the shot (ie. 'mod', 'rig', 'tex', 'mat')
        :param variant: Optional - specify a variant to use
        :param override: Optional - specifiy an override for the variant and task.
                        use a path relative to the
        :return:
        """
        data = self._data
        if data['elements'].has_key(elementCode):
            if task: data['elements'][elementCode]['task'] = task
            if variant: data['elements'][elementCode]['variant'] = variant
            if override: data['elements'][elementCode]['override'] = override
            self.setData(data)
        else:
            raise KeyError('Element "{}" is not part of this shot'.format(element))


if __name__ == '__main__':
    sh = Shot(
        "/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio/shows/TEST/work/sequences/seq/010/0010")
    # sh.add_task('new')

    # print sh.add_element('testCharacter', 'char', 'rig')
    # sh.get_element_data('testCharacter')
    # sh.set_element('testCharacter1', task='mod', override='rig/test.ma')

    # elements = sh.get_elements()

    # sh.rm_element('testCharacter')
