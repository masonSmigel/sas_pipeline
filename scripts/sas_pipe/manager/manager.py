"""
Manager functions for creating and editing entities
"""
import os
import shutil
from collections import OrderedDict
import sas_pipe.common as common
import sas_pipe.utils.osutil as osutil
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.environment as environment
import sas_pipe.manager.user_prefs as user_prefs

import sas_pipe.entities.studio
import sas_pipe.entities.show
import sas_pipe.entities.element
import sas_pipe.entities.sequence
import sas_pipe.entities.shot


class WorkspaceError(Exception): pass


class UserError(Exception): pass


def initalizeEnv():
    """
    :return:
    """
    if not environment.getEnv('root'):
        prefs_root = user_prefs.UserPrefs.get_root()
        if prefs_root:
            environment.setEnv('root', prefs_root)
        else:
            raise WorkspaceError('No root is set. Set a root to continue')

    show = user_prefs.UserPrefs.get_currentShow()
    if show:
        environment.setEnv('show', show)
    else:
        raise WorkspaceError('No show is set. Set a show to continue')

    # if we have a show and a root, we can set the rest of our enviornment variables
    environment.setEnv('shows_path', os.path.join(environment.getEnv('root'), 'shows'))
    environment.setEnv('depts_path', os.path.join(environment.getEnv('root'), 'depts'))
    environment.setEnv('show_path', os.path.join(environment.getEnv('shows_path'), environment.getEnv('show')))
    environment.setEnv('rel_path', os.path.join(environment.getEnv('show_path'), 'rel'))
    environment.setEnv('work_path', os.path.join(environment.getEnv('show_path'), 'work'))
    environment.setEnv('elm_work_path', os.path.join(environment.getEnv('work_path'), 'elements'))
    environment.setEnv('seq_work_path', os.path.join(environment.getEnv('work_path'), 'sequences'))
    environment.setEnv('elm_rel_path', os.path.join(environment.getEnv('rel_path'), 'elements'))
    environment.setEnv('seq_rel_path', os.path.join(environment.getEnv('rel_path'), 'sequences'))


def mkstudio(studio, path):
    """
    This function creates a new studio
    :param studio: name of the studio to create
    :type studio: str
    :param path: path to create a studio at.
    :return:
    """
    studio_path = osutil.clean_path(os.path.join(path, studio))
    if os.path.exists(studio_path):
        raise UserError('Studio already exists at : {}'.format(path))

    os.mkdir(studio_path)
    os.mkdir(os.path.join(studio_path, 'depts'))
    os.mkdir(os.path.join(studio_path, 'shows'))

    for dept in common.DEPTS:
        os.mkdir((os.path.join(studio_path, 'depts', dept)))

    # tag the folder as a studio root
    pipeutils.addEntityTag(studio_path, 'studio')

    return sas_pipe.entities.studio.Studio(studio_path)


def rmstudio(path):
    """
    This function removes a studio
    :param path: path to studio to remove
    :return:
    """
    if sas_pipe.entities.studio.isStudio(path):
        shutil.rmtree(path)
    else:
        raise TypeError('{} is not a studio.'.format(path))


# create a show
def mkshow(show, assetTypes=None, sequenceTypes=None):
    """
    Make a new show. This will also set the active show to the new show.
    :param show: name of the show to remove. This will be all uppercased
    :param assetTypes:
    :param sequenceTypes:
    :return: show element
    """
    show_path = osutil.clean_path(os.path.join(environment.getEnv('shows_path'), show.upper()))
    if os.path.exists(show_path):
        raise UserError('show already exists: {}'.format(show))

    # set the show to re-initialize the enviornment
    user_prefs.UserPrefs.set_current_show(show.upper())
    initalizeEnv()
    os.mkdir(environment.getEnv('show_path'))
    os.mkdir(environment.getEnv('work_path'))
    os.mkdir(environment.getEnv('rel_path'))
    os.mkdir(environment.getEnv('elm_work_path'))
    os.mkdir(environment.getEnv('seq_work_path'))
    os.mkdir(environment.getEnv('elm_rel_path'))
    os.mkdir(environment.getEnv('seq_rel_path'))

    # tag the folder as a show
    pipeutils.addEntityTag(show_path, 'show')

    # add the show to the studio data
    studio_entity = sas_pipe.entities.studio.Studio(environment.getEnv('root'))
    studio_entity.add_show(show.upper())

    # create a manifest file
    show_entity = sas_pipe.entities.show.Show(show_path)
    if assetTypes:
        show_entity.set_assetTypes(assetTypes)
    if sequenceTypes:
        show_entity.set_sequenceTypes(sequenceTypes)

    for type in show_entity._data['asset_types']:
        os.mkdir(os.path.join(environment.getEnv('elm_work_path'), type))
        os.mkdir(os.path.join(environment.getEnv('elm_rel_path'), type))

    for type in show_entity._data['sequence_types']:
        os.mkdir(os.path.join(environment.getEnv('seq_work_path'), type))
        os.mkdir(os.path.join(environment.getEnv('seq_rel_path'), type))
    return show_entity


def rmshow(show):
    """
    remove a show
    :param show: name of the show to remove
    """
    show_path = os.path.join(environment.getEnv('shows_path'), show.upper())
    if sas_pipe.entities.show.isShow(show_path):
        shutil.rmtree(show_path)
        studio_entity = sas_pipe.entities.studio.Studio(environment.getEnv('root'))
        studio_entity.rm_show(show.upper())
    else:
        raise TypeError('{} is not a show.'.format(show_path))


def mkelm(asset, type, var_data=None):
    """
    Make a new element
    :param asset: name of asset to create
    :param type: type of asset
    :param var_data: Optional - dictionary of variant data.
                    ex {'base' : {'mod': 'mod', 'rig': 'rig', 'tex': 'look/tex', 'mat' : 'look/mat'}}
    :return: element entity
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))

    if type not in show_entity.assetTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.assetTypes))
    elm_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path'), type, asset))
    elm_rel_path = osutil.clean_path(os.path.join(environment.getEnv('elm_rel_path'), type, asset))

    # setup the asset
    os.makedirs(elm_work_path)
    os.makedirs(elm_rel_path)

    # Tag the folder as a show
    pipeutils.addEntityTag(elm_work_path, 'element')
    pipeutils.addEntityTag(elm_rel_path, 'element')

    elm_entity = sas_pipe.entities.element.Element(elm_work_path)

    # if we pass var_data then add that to the elm_entity
    if var_data:
        elm_entity.set_tasks(var_data.keys())
        elm_entity.set_variants(var_data)

    variant_data = elm_entity.get_variant_tasks('base')
    for task in elm_entity.get_tasks():
        os.makedirs(os.path.join(elm_entity.work_path, variant_data[task]))
        os.makedirs(os.path.join(elm_entity.rel_path, variant_data[task]))

    return elm_entity


def rmelm(asset, type):
    """
    Remove an element
    :param asset: name of asset to delete
    :param type: type of asset
    """
    elm_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path'), type, asset))
    elm_rel_path = osutil.clean_path(os.path.join(environment.getEnv('elm_rel_path'), type, asset))

    if sas_pipe.entities.element.isElement(elm_work_path) and sas_pipe.entities.element.isElement(elm_rel_path):
        shutil.rmtree(elm_work_path)
        shutil.rmtree(elm_rel_path)


def mkshot(seq, shot, type=None, var_data=None):
    """
    Create a new show
    :param seq: name of the sequence
    :param shot: name of the shot
    :param type: type of shot to create
    :param var_data: Optional - dictionary of variant data.
    :return:
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    if type is None: type = 'seq'
    if type not in show_entity.sequenceTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.sequenceTypes))

    shot_work_path = osutil.clean_path(os.path.join(environment.getEnv('seq_work_path'), type, seq, shot))
    shot_rel_path = osutil.clean_path(os.path.join(environment.getEnv('seq_rel_path'), type, seq, shot))

    # setup the asset
    os.makedirs(shot_work_path)
    os.makedirs(shot_rel_path)

    # Tag the folder as a show
    pipeutils.addEntityTag(shot_work_path, 'shot')
    pipeutils.addEntityTag(shot_rel_path, 'shot')

    shot_entity = sas_pipe.entities.shot.Shot(shot_work_path)

    # if we pass var_data then add that to the elm_entity
    if var_data:
        pass
        # elm_entity.set_tasks(var_data.keys())
        # elm_entity.set_variants(var_data)


def rmshot(seq, shot, type=None):
    """
    Remove an element

    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    if type is None: type = 'seq'
    if type not in show_entity.sequenceTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.sequenceTypes))

    shot_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path'), type, seq, shot))
    shot_rel_path = osutil.clean_path(os.path.join(environment.getEnv('elm_rel_path'), type, seq, shot))

    if sas_pipe.entities.shot.isShot(shot_work_path) and sas_pipe.entities.shot.isShot(shot_rel_path):
        shutil.rmtree(shot_work_path)
        shutil.rmtree(shot_rel_path)


if __name__ == '__main__':
    import json

    user_prefs.UserPrefs.set_root('/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio')
    user_prefs.UserPrefs.set_current_show('TEST')

    initalizeEnv()
    # print mkstudio('testStudio', '/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root')
    # show = mkshow('TEST')

    try:
        rmelm('testA', 'prop')
        # rmshot('010', '0010')
    except:
        pass

    elm = mkelm('testA', 'prop')
    # shot = mkshot('010', '0010')

    # rmshow('TEST')

    # print json.dumps(environment.getAll(), indent=2)
