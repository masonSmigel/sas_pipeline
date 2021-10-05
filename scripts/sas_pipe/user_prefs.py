import sas_pipe.utils.data.abstract_data as abstract_data
import sas_pipe.utils.osutil as os_util
import os

PREFS_PATH = os.path.join(os.path.expanduser("~"), 'sas_user.pref')

DEFAULT_DATA = {'root': ''}


class UserPrefs(object):
    _prefs_obj = None

    @classmethod
    def prefs_obj(cls):
        if not cls._prefs_obj:
            cls._prefs_obj = abstract_data.AbstractData()

        if os.path.exists(PREFS_PATH):
            cls._prefs_obj.read(PREFS_PATH)
        else:
            cls._prefs_obj.setData(DEFAULT_DATA)
            cls._prefs_obj.write(PREFS_PATH)
        return cls._prefs_obj

    @classmethod
    def set_root(cls, root_path):
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        data['root'] = root_path
        prefs.setData(data)
        prefs.write(PREFS_PATH)

    @classmethod
    def set_current_show(cls, show):
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        data['current_show'] = show
        prefs.setData(data)
        prefs.write(PREFS_PATH)

    @classmethod
    def get_root(cls):
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        if data.has_key('root'):
            return data['root']
        return None

    @classmethod
    def get_currentShow(cls):
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        if data.has_key('current_show'):
            return data['current_show']
        return None
