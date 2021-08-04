""" This module contrains the Pipeline Manager class"""
import os

import sas_pipe.shared.common as common
import sas_pipe.shared.data.abstract_data as abstract_data
import sas_pipe.shared.naming as naming
import sas_pipe.shared.os_utils as os_util
from sas_pipe.shared.entities import asset_, shot_, sequence_
from sas_pipe.shared.logger import Logger

PREFS_PATH = os.path.join(os_util.get_parent(os.path.abspath(__file__), 4), 'userPrefs.pref')


class PipelineManager(object):
    def __init__(self, root_path=None):
        self.root_path = root_path

        # setup and load user_prefs
        # settings and prefs
        self.settings_obj = None
        self.settings = None
        self.prefs_obj = None
        self.prefs = None

        self.depts_path = None
        self.shows_path = None

        self.current_show = None
        self.show_path = None

        # These "modes" are relative to the show
        # They will be created later if a show is provided
        self.rel_path = None
        self.work_path = None

        self.asset_work_path = None
        self.seq_work_path = None
        self.asset_rel_path = None
        self.seq_rel_path = None

        # if no rootpath is provided locate the userPrefs.pref
        self.__load_user_prefs()
        if self.root_path is None:
            if PipelineManager.validate_root():
                self.root_path = self.prefs['root']
            else:
                Logger.critical('No root path provided or found. Use set_root_path to to set a root')

        if self.root_path:
            self.depts_path = os.path.join(self.root_path, common.DEPTS)
            self.shows_path = os.path.join(self.root_path, common.SHOWS)
            self.validate_project()

    def validate_project(self):
        """ Make sure all paths exist """
        if not os.path.exists(self.root_path):
            Logger.error("root path does not exist.")
            return
        else:
            os_util.validate_directory(self.depts_path, create=True)
            os_util.validate_directory(self.shows_path, create=True)
            if self.validate_show():
                Logger.debug('Creating show children directories')
                self.update_show_children()

    def validate_show(self):
        """Check if the show exists """
        if self.current_show:
            self.set_show(self.current_show)
            if os_util.validate_directory(self.show_path):
                return True
            else:
                Logger.warning(
                    "{} show does not exist. use the add_show() method to create a new show".format(self.current_show))
                return False
        return False

    def set_show(self, show):
        """Set the show variable for the class. All paths will be updated """
        self.current_show = show
        self.show_path = os.path.join(self.shows_path, self.current_show)

        data = self.prefs_obj.getData()
        data['lastShow'] = show
        self.prefs_obj.write(PREFS_PATH)

        self.update_settings()
        self.update_show_children()

    def update_settings(self):
        """ Update the settings attribute """
        self.settings_obj = abstract_data.AbstractData()
        settings_path = os.path.join(self.show_path, 'settings.json')
        if os.path.exists(settings_path):
            self.settings_obj.read(settings_path)
            self.settings = self.settings_obj.getData()
        else:
            default_data = {'shot_tasks': ['audio', 'lay', 'anim', 'crowd', 'fx', 'sim', 'lgt', 'comp'],
                            'sequence_types': ['pub', 'seq'],
                            'asset_tasks': ['mod', 'rig', 'look', 'conc'],
                            'asset_types': ['char', 'prop', 'set', 'setPeice'],
                            'other_depts': ['core'],
                            'maya_file_type': 'ma'}

            self.settings_obj.setData(default_data)
            self.settings_obj.write(settings_path)

        self.settings = self.settings_obj.getData()

    def update_show_children(self):
        """ Update show children """
        self.rel_path = os.path.join(self.show_path, common.REL)
        self.work_path = os.path.join(self.show_path, common.WORK)

        self.asset_work_path = os.path.join(self.work_path, common.ASSETS)
        self.seq_work_path = os.path.join(self.work_path, common.SEQUENCES)
        self.asset_rel_path = os.path.join(self.rel_path, common.ASSETS)
        self.seq_rel_path = os.path.join(self.rel_path, common.SEQUENCES)

        os_util.validate_directories([self.depts_path] +
                                 [os.path.join(self.depts_path, type) for type in self.settings['asset_tasks']] +
                                 [os.path.join(self.depts_path, type) for type in self.settings['shot_tasks']] +
                                 [os.path.join(self.depts_path, type) for type in self.settings['other_depts']])

        os_util.validate_directories([self.asset_work_path, self.asset_rel_path, self.seq_work_path, self.seq_rel_path] +
                                 [os.path.join(d, type) for type in self.settings['asset_types'] for d in
                                  [self.asset_work_path, self.asset_rel_path]] +
                                 [os.path.join(d, type) for type in self.settings['sequence_types'] for d in
                                  [self.seq_work_path, self.seq_rel_path]])

    def add_show(self, show_name):
        """
        Add a new show
        :param show_name: name of the show to add
        """
        return os_util.create_directory(os.path.join(os.path.join(self.shows_path, show_name.upper())))

    def add_asset(self, asset, type):
        """
        Create new asset
        :param asset: name of the asset
        :type asset: str

        :param type: asset type
        :type type: str

        :returns: path to asset
        :rtype: str
        """
        for mode in [True, False]:
            path = self.__build_asset_path(type=type, rel=mode, asset=asset)
            if not os.path.exists(path):
                os_util.create_directory(path)
                Logger.info('New asset: {} created with type {}'.format(asset, type))
                for task in self.settings['asset_tasks']:
                    os_util.create_directory(os.path.join(path, task))
            else:
                Logger.warning("Asset '{}' already exists in show {}".format(asset, self.current_show))

    def add_sequence(self, sequence, type):
        """
        Create new sequence
        :param sequence: sequence to create
        :type sequence: str

        :param type: sequence type
        :type type: str

        :returns: path to sequence
        :rtype: str
        """
        for mode in [True, False]:
            path = self.__build_seq_path(sequence=sequence, type=type, rel=mode)
            if not os.path.exists(path):
                Logger.info('New sequence: {} created with type {}'.format(sequence, type))
                os_util.create_directory(os.path.join(path))
            else:
                Logger.warning("Sequence '{}' already exists in show {}".format(sequence, self.current_show))

    def add_shot(self, shot, sequence, type=None):
        """
        Create new shot
        :param shot: name of the asset
        :type shot: str

        :param sequence: sequence to put the shot in
        :type sequence: str

        :param type: type of sequence
        :type type: str
        """
        for mode in [True, False]:
            path = self.__build_shot_path(sequence=sequence, type=type, shot=shot, rel=mode)
            if not os.path.exists(path):
                Logger.info('New shot: {} created under sequence {}/{}'.format(shot, type, sequence))
                for task in self.settings['shot_tasks']:
                    os_util.create_directory(os.path.join(path, task))
            else:
                Logger.warning("Shot '{}/{}' already exists in show {}".format(sequence, shot, self.current_show))

    # get methods for important directories
    def get_shows(self, base_only=False):
        """
        :param base_only: get the full path of an object
        :type base_only: bool

        :return: Return a items of all shows
        :rtype: list
        """
        return self.get_many(self.shows_path, base_only=base_only)

    def get_show(self, show, base_only=False):
        """
        Get the path of a specific show
        :param show:
        :param base_only:
        :return:
        """
        return self.get_one(show, self.get_shows(base_only=True), base_only=base_only)

    def get_depts(self, base_only=False):
        """
        :param base_only: get the full path of an object
        :type base_only: bool

        :return: Return a items of all departments
        :rtype: list
        """
        return self.get_many(self.depts_path, base_only=base_only)

    def get_assets(self, type=None, rel=False, base_only=False):
        """
        List all assets. If a type is provided get only assets of that type
        :param type: Optional - Asset type to return.
        :type type: str

        :param rel: If True will items assets in release path. False will return assets in the working path
        :type rel: bool

        :param base_only: get the full path of an object
        :type base_only: bool

        :return: List of assets
        :rtype: list
        """
        result = list()
        if type:
            result.extend(self.get_many(self.__build_asset_path(type=type, rel=rel), base_only=base_only))
        else:
            for type in self.settings['asset_types']:
                result.extend(self.get_many(self.__build_asset_path(type=type, rel=rel), base_only=base_only))

        return sorted(result)

    def get_asset(self, asset=None, type=None, rel=False, base_only=False):
        """
        Get a specific asset based on name
        :param asset: Asset to get
        :type asset: str

        :param type: Optional - type of the asset. May be required if multiple assets have the same name
        :type type: str

        :param rel: If True will items assets in release path. False will return assets in the working path
        :type rel: bool

        :param base_only: get the full path of an object
        :type base_only: bool

        :return:
        """
        result = list()
        if type:
            result.extend(self.get_one(asset, self.__build_asset_path(type=type, rel=rel), base_only=base_only))
        else:
            for type in self.settings['asset_types']:
                result.extend(self.get_one(asset, self.__build_asset_path(type=type, rel=rel), base_only=base_only))
        if len(result) > 0:
            return asset_.Asset(common.getFirstIndex(result))
        else:
            return None

    def get_sequences(self, type=None, rel=False, base_only=False):
        """
        List all Sequences. If a type is provided get only sequences of that type
        :param type: Optional - Sequence type to return.
        :type type: str

        :param rel: If True will items sequences in release path. False will return sequences in the working path
        :type rel: bool

        :param base_only: get the full path of an object
        :type base_only: bool

        :return: List of sequences
        :rtype: list
        """
        result = list()
        if type:
            result.extend(self.get_many(self.__build_seq_path(type=type, rel=rel), base_only=base_only))
        else:
            for type in self.settings['sequence_types']:
                result.extend(self.get_many(self.__build_seq_path(type=type, rel=rel), base_only=base_only))
        return sorted(result)

    def get_sequence(self, sequence, type=None, rel=False, base_only=False):
        """
        Get a specicific sequence based on sequence name
        :param sequence: sequence to get
        :type sequence: str

        :param type: Optional - Sequence type to return.
        :type type: str

        :param rel: If True will items sequences in release path. False will return sequences in the working path
        :type rel: bool

        :param base_only: get the full path of an object
        :type base_only: bool

        :return: path to sequence
        :rtype: list
        """
        result = list()
        if type:
            result.extend(self.get_one(sequence, self.__build_seq_path(type=type, rel=rel), base_only=base_only))
        else:
            for type in self.settings['sequence_types']:
                result.extend(self.get_one(sequence, self.__build_seq_path(type=type, rel=rel), base_only=base_only))

        if len(result) > 0:
            return sequence_.Sequence(common.getFirstIndex(result))
        else:
            return None

    def get_shots(self, sequence, type=None, rel=False, base_only=False):
        """
        List all Shots in a sequence.
        :param sequence: Sequence to get shots from
        :type sequence: str

         :param type: type of sequence
         :type type: str

        :param rel: If True will items shots in release path. False will return shots in the working path
        :type rel: bool

        :return: List of shots
        :rtype: list

        :param base_only: get the  path of an object
        :type base_only: bool
        """
        result = list()
        path = self.__build_shot_path(sequence=sequence, type=type, rel=rel)
        if path:
            result.extend(
                self.get_many(self.__build_shot_path(sequence=sequence, type=type, rel=rel), base_only=base_only))
        return sorted(result)

    def get_shot(self, shot, sequence, type=None, rel=False, base_only=False):
        """
        :param shot: name of the shot to get
        :type shot: str

        :param sequence: Sequence to get shots from
        :type sequence: str

        :param type: type of sequence
        :type type: str

        :param rel: If True will items sequences in release path. False will return sequences in the working path
        :type rel: bool

        :param base_only: get the full path of an object
        :type base_only: bool

        :return: path to sequence
        :rtype: list
        """
        result = list()
        path = self.__build_shot_path(sequence=sequence, type=type, rel=rel)
        if path:
            result.extend(
                self.get_one(shot, self.__build_shot_path(sequence=sequence, type=type, rel=rel), base_only=base_only))

        if len(result) > 0:
            return shot_.Shot(common.getFirstIndex(result))
        else:
            return None

    def save_new_version(self, entity, task, file_type, warble=None):
        """
        Save an entity at the next available version.

        :param entity: entity to save the version as
        :type entity: Entity

        :param task: task to save the file under
        :type task: str

        :param file_type: file type of the save file
        :type file_type: str

        :param warble: warble to add the the name
        :type warble: str
        """

        if isinstance(entity, (asset_.Asset, shot_.Shot)):
            filename = naming.get_unique_filename(work=True, base=entity.name, task=task, warble=warble, ext=file_type,
                                                  path=os.path.join(entity.work_path, task))
            return self._save_file(os.path.join(entity.work_path, task, filename))
        else:
            Logger.error("Entity '{}' is not of type Shot or Asset.".format(entity))

    def publish_file(self, entity, task, file_type, warble=None):
        """
        Publish an entity to the release directory

        :param entity: entity to save the version as
        :type entity: Entity

        :param task: task to save the file under
        :type task: str

        :param file_type: file type of the save file
        :type file_type: str

        :param warble: warble to add the the name
        :type warble: str
        """
        if isinstance(entity, (asset_.Asset, shot_.Shot)):
            filename = naming.get_unique_filename(work=False, base=entity.name, task=task, warble=warble, ext=file_type,
                                                  path=os.path.join(entity.rel_path, task))
            return self._save_file(os.path.join(entity.rel_path, task, filename))

        else:
            Logger.error("Entity '{}' is not of type Shot or Asset.".format(entity))

    def get_one(self, item, dir, base_only=False):
        """
        Get one item from a path
        :param item: Item to get
        :param dir: path to look in
        :param base_only: return full path of an object
        :return:
        """
        for i in self.get_many(dir=dir, base_only=True):
            if i == item:
                if base_only:
                    return i
                else:
                    return common.toList(os.path.join(dir, i))
        return list()

    def get_many(self, dir, base_only=False):
        """
        Get all items from a path
        :param dir: path to look in
        :type dir: str

        :param base_only: get path relative to the root path
        :type base_only: bool

        :return: items
        :rtype: list
        """
        abs_dir = os.path.join(self.root_path, dir)
        contents = [f for f in os.listdir(abs_dir) if os.path.isdir(os.path.join(dir, f))]
        if base_only:
            return [one.encode('UTF8') for one in contents]
        else:
            many = [os.path.relpath(os.path.join(dir, content), self.root_path) for content in contents]
            return [one.encode('UTF8') for one in many]

    # Utility methods
    def get_relative_path(self, path, start=None):
        """
        Get the path relative to the start. If start is None use project root
        :param path: path to convert
        :param start: path to start from
        :return: relative path
        """
        if os.path.isabs(path):
            if not start:
                start = self.root_path
            return os.path.relpath(path, start)
        else:
            return path

    def parse_path(self, path):
        """
        parse the path and return important information in a dictonary
        :param path: path to parse
        :return: dictonary of important information
        """

        normpath = os.path.normpath(path).replace('\\', '/')
        result = dict()
        rel_path = self.get_relative_path(normpath)
        path_split = rel_path.split(os.sep)
        if common.tryIndex(path_split, 0) == 'shows':
            result['show'] = common.tryIndex(path_split, 1)
            result['mode'] = common.tryIndex(path_split, 2)
            result['stage'] = common.tryIndex(path_split, 3)
            if result['stage'] == common.ASSETS:
                result['type'] = common.tryIndex(path_split, 4)
                result['asset'] = common.tryIndex(path_split, 5)
                result['task'] = common.tryIndex(path_split, 6)
                result['file'] = common.tryIndex(path_split, 7)
                if result['file']:
                    result['file_type'] = result['file'].split('.')[-1]
            if result['stage'] == common.SEQUENCES:
                result['type'] = common.tryIndex(path_split, 4)
                result['sequence'] = common.tryIndex(path_split, 5)
                result['shot'] = common.tryIndex(path_split, 6)
                result['task'] = common.tryIndex(path_split, 7)
                result['file'] = common.tryIndex(path_split, 8)
            if result['file']:
                result['file_type'] = result['file'].split('.')[-1]

        elif common.tryIndex(path_split, 0) is 'depts':
            # TODO: setup how departments work
            pass

        return result

    def is_release(self, path):
        """
        :param path: Check if the path is in the release or working path of a show
        :return:
        """
        parsed_path = self.parse_path(path)
        if parsed_path['mode'] == 'rel':
            return True
        return False

    # path Builders
    def __build_asset_path(self, type=None, rel=False, asset=None):

        mode_path = self.asset_rel_path if rel else self.asset_work_path
        if type in self.settings['asset_types']:
            if asset:
                return os.path.join(mode_path, type, asset)
            else:
                return os.path.join(mode_path, type)
        else:
            Logger.error(
                "'{}' is not a valid asset type. valid types are: {}".format(type, self.settings['asset_types']))
        return None

    def __build_seq_path(self, type=None, rel=False, sequence=None):

        mode_path = self.seq_rel_path if rel else self.seq_work_path
        if type in self.settings['sequence_types']:
            if sequence:
                return os.path.join(mode_path, type, sequence)
            else:
                return os.path.join(mode_path, type)
        else:
            Logger.error(
                "'{}' is not a valid sequence type. valid types are: {}".format(type, self.settings['sequence_types']))
        return None

    def __build_shot_path(self, sequence, type=None, rel=False, shot=None):

        mode_path = self.seq_rel_path if rel else self.seq_work_path
        if not type:
            type = os_util.locate(sequence, [os.path.join(mode_path, type) for type in self.settings['sequence_types']],
                              base_only=True)
        if type in self.settings['sequence_types']:
            if shot:
                return os.path.join(mode_path, type, sequence, shot)
            else:
                return os.path.join(mode_path, type, sequence)
        else:
            Logger.error("The sequence: '{}' could not be found. exiting sequences are: {}"
                         .format(sequence, self.get_sequences(base_only=True)))
        return None

    # user Prefs Stuff
    def __load_user_prefs(self):
        self.prefs_obj = abstract_data.AbstractData()
        if os.path.exists(PREFS_PATH):
            self.prefs_obj.read(PREFS_PATH)
        else:
            default_data = {'root': ''}
            if self.root_path:
                default_data = {'root': self.root_path}
            self.prefs_obj.setData(default_data)
            self.prefs_obj.write(PREFS_PATH)

        self.prefs = self.prefs_obj.getData()

    @staticmethod
    def set_root_path(root_path):
        prefs = abstract_data.AbstractData()
        data = dict()
        data['root'] = root_path
        prefs.setData(data)
        prefs.write(PREFS_PATH)

    @staticmethod
    def validate_root(log=False):
        if os.path.exists(PREFS_PATH):
            prefs = abstract_data.AbstractData()
            prefs.read(PREFS_PATH)
            data = prefs.getData()
            if data.has_key('root'):
                if os.path.exists(data['root']):
                    if log:
                        Logger.info("Root path: {}".format(data['root']))
                    return True
        return False

    def _save_file(self, path):
        """
        Code to save a file, unique to dcc. Reimplement in subclasses
        """
        return path

    def _open_file(self, path):
        """
        Code to open a file, unique to dcc. Reimplement in subclasses
        """
        return path


if __name__ == '__main__':
    pipe = PipelineManager('/Users/masonsmigel/Documents/jobs/animAide_job/pipeline/projects_root/SAS')
