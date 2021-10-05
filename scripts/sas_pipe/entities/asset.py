import sas_pipe.entities.entity as entity
import os
from collections import OrderedDict
import sas_pipe.utils.data.asset_data as asset_data
import sas_pipe.utils.osutil as os_utils


class Asset(entity.Entity):
    base_data = OrderedDict({'variant': False,
                             'mod': 'mod',
                             'rig': 'rig',
                             'tex': 'look/tex',
                             'mat': 'look/mat',
                             })

    def __init__(self, path):
        super(Asset, self).__init__(path)

    def assign_lookdev(self):
        print('Assign lookdev to {}'.format(self.name))
        pass

    def add_variant(self, variant, variant_data=None):
        """
        Add a variant
        :param variant: name of the variant
        :param variant_data: data of the variant
        :return:
        """
        data_obj = asset_data.EntityData()
        data_obj.read(self.manifest_path)
        data_obj.add_variant(variant=variant, data=variant_data)
        data_obj.write(self.manifest_path)

        # create folders for stuff
        for task in variant_data.keys():
            if task is not 'variant':
                if not os.path.isdir(os.path.join(self.work_path, variant_data[task])):
                    os_utils.create_directory(os.path.join(self.work_path, variant_data[task]))
                    os_utils.create_directory(os.path.join(self.rel_path, variant_data[task]))

        self.read_manifest()

    def read_variant(self, task, variant):
        if self.manifest_data.has_key(variant):
            if self.manifest_data[variant].has_key(task):
                return self.manifest_data[variant][task]
            else:
                return self.manifest_data['base'][task]
        else:
            return self.manifest_data['base'][task]

    def get_file(self):
        if self.mode == 'rel':
            return self.get_rel()
        else:
            return self.get_work()

    def get_work(self):
        """
        Get the file with the highest index from a specified task. Always returns file in the working path
        :return: highest version in the task
        """

        path = self.task_path()

        if os.path.exists(path):
            file_path = None
            if self._get_file_from_directory(path):
                file_path = os.path.join(path, self._get_file_from_directory(path))
            return path, file_path
        else:
            return None, None

    def get_rel(self):
        """
        get the publish file if one exists
        :return: published file for the specified task
        """
        path = self.task_path()

        if os.path.exists(path):
            file_path = None
            if os_utils.is_file(self.read_variant(task=self.task, variant=self.variant)):
                file_path = os.path.join(path,
                                         os.path.basename(self.read_variant(task=self.task, variant=self.variant)))

            elif self._get_file_from_directory(path):
                file_path = os.path.join(path, self._get_file_from_directory(path))
            return path, file_path
        else:
            return None, None

    def task_path(self):
        mode_path = self.rel_path if self.mode == 'rel' else self.work_path
        variant_data = self.read_variant(task=self.task, variant=self.variant)
        if os_utils.is_file(variant_data):
            return os.path.dirname(os.path.join(mode_path, variant_data))
        else:
            return os.path.join(mode_path, variant_data)


if __name__ == '__main__':
    e = Asset('/Users/masonsmigel/Dropbox (Neko Productions)/SAS/shows/DEMO/work/assets/char/mrCube')
    e.add_variant('damaged', {"mod": "mod/damaged/mrCube_damaged_mod.ma"})

    e.set_mode('work')
    e.set_variant('damaged')
    e.set_task('tex')

    print e.get_file()

    e.set_task('mod')
    print e.get_file()
    # e.set_mode('rel')
    # print e.get_file()
    # print e.get_rel()
