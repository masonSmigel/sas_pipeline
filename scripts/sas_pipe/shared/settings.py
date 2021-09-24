"""
settings class
"""

DEBUG = False


class Settings(object):
    _setting_obj = None

    @classmethod
    def settings_obj(cls):
        if not cls._setting_obj:
            if cls.logger_exists():
                cls._setting_obj = logging.getLogger(cls.LOGGER_NAME)
            else:
                cls._setting_obj = logging.getLogger(cls.LOGGER_NAME)
                cls._setting_obj.setLevel(cls.LEVEL_DEFAULT)
                cls._setting_obj.propagate = cls.PROPAGATE_DEFAULT

        return cls._setting_obj
