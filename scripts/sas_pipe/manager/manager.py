"""
Manager functions for creating and editing entities
"""
import os
import sas_pipe.utils.osutil as osutil
import sas_pipe.environment as environment
from sas_pipe.user_prefs import UserPrefs


class WorkspaceError(Exception): pass


def initalizeEnv():
    """
    :return:
    """
    if not environment.getEnv('root'):
        prefs_root = UserPrefs.get_root()
        if prefs_root:
            environment.setEnv('root', prefs_root)
        else:
            raise WorkspaceError('No root is set. Set a root to continue')

    if not environment.getEnv('show'):
        show = UserPrefs.get_currentShow()
        if show:
            environment.setEnv('show', show)
        else:
            raise WorkspaceError('No show is set. Set a show to continue')

    # if we have a show and a root, we can set the rest of our enviornment variables
    environment.setEnv('shows_path', os.path.join(environment.getEnv('root'), 'shows'))
    environment.setEnv('depts_path', os.path.join(environment.getEnv('root'), 'depts'))
    environment.setEnv('current_show_path', os.path.join(environment.getEnv('shows_path'), environment.getEnv('show')))
    environment.setEnv('rel_path', os.path.join(environment.getEnv('current_show_path'), 'rel'))
    environment.setEnv('work_path', os.path.join(environment.getEnv('current_show_path'), 'work'))
    environment.setEnv('asset_work_path', os.path.join(environment.getEnv('work_path'), 'asset'))
    environment.setEnv('seq_work_path', os.path.join(environment.getEnv('work_path'), 'seq'))
    environment.setEnv('asset_rel_path', os.path.join(environment.getEnv('rel_path'), 'asset'))
    environment.setEnv('seq_rel_path', os.path.join(environment.getEnv('rel_path'), 'seq'))


def mkstudio(studio, path):
    """
    This function creates a new studio
    :param studio: name of the studio to create
    :type studio: str
    :param path: path to create a studio at.
    :return:
    """
    studio_path = osutil.clean_path(os.path.join(path, studio))
    osutil.v

if __name__ == '__main__':
    # UserPrefs.set_current_show('TEST')
    import json

    initalizeEnv()
    print json.dumps(environment.getAll(), indent=2)
