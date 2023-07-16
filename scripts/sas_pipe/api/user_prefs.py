import sas_pipe.utils.data.abstract_data as abstract_data
import sas_pipe.utils.osutil as os_util
import sas_pipe.common as common
import os

PREFS_PATH = os.path.join(os.path.expanduser("~"), 'sas_user.pref')

DEFAULT_DATA = {'root': ''}


class UserPrefs(object):
    _prefs_obj = None

    # TODO: update to use something else cause this is not working when the file is changed.
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

        UserPrefs.append_studio(root_path)

    @classmethod
    def set_current_show(cls, show):
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        data['lastShow'] = show
        prefs.setData(data)
        prefs.write(PREFS_PATH)

    @classmethod
    def get_root(cls):
        """Get the current studio root"""
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        if 'root' in list(data.keys()):
            return data['root']
        return None

    @classmethod
    def get_currentShow(cls):
        """get the current show"""
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        if 'lastShow' in list(data.keys()):
            return data['lastShow']
        return None

    @classmethod
    def set_studios(cls, rootList):
        """get a list of avialable studio roots"""
        prefs = cls.prefs_obj
        data = prefs.read(PREFS_PATH)
        data['rootsList'] = common.toList(rootList)
        prefs.setData(data)
        prefs.write(PREFS_PATH)

    @classmethod
    def append_studio(cls, studio):
        """Append a studio to the studio list"""

        if studio not in UserPrefs.get_studios():
            prefs = cls.prefs_obj()
            data = prefs.read(PREFS_PATH)
            if 'rootsList' in list(data.keys()):
                studiosList = data['rootsList']
            else:
                studiosList = list()
            studiosList.append(studio)

            data['rootsList'] = studiosList
            prefs.setData(data)
            prefs.write(PREFS_PATH)

    @classmethod
    def get_studios(cls):
        """Get studios"""
        prefs = cls.prefs_obj()
        data = prefs.read(PREFS_PATH)
        if 'rootsList' in list(data.keys()):
            return data['rootsList']
        return list()


