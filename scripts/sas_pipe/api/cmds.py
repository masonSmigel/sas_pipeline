"""
Manager functions for creating and editing entities
"""
import os
import re
import shutil
from collections import OrderedDict
import sas_pipe.common as common
import sas_pipe.utils.osutil as osutil
import sas_pipe.utils.pipeutils as pipeutils
import sas_pipe.environment as environment
import sas_pipe.api.user_prefs as user_prefs

import sas_pipe.entities.studio
import sas_pipe.entities.show
import sas_pipe.entities.element
import sas_pipe.entities.sequence
import sas_pipe.entities.shot


class WorkspaceError(Exception): pass


class UserError(Exception): pass


# ENVIORNMENT
def setstudio(path):
    """
    Set the studio path
    :param path: path to the studio
    :return:
    """
    path = os.path.realpath(path)

    if not sas_pipe.entities.studio.isstudio(path=path):
        raise UserError('The path "{}" is not a studio. Please pick a valid studio'.format(path))
    user_prefs.UserPrefs.set_root(path)

    # setup the enviornment variables
    environment.setEnv('root', path)

    environment.setEnv('shows_path', os.path.join(environment.getEnv('root'), 'shows'))
    environment.setEnv('depts_path', os.path.join(environment.getEnv('root'), 'depts'))
    return path


def setshow(show):
    """
    Set the show
    :param show:
    :return:
    """
    # set the root enviornment variables
    if not environment.getEnv('root'):
        prefs_root = user_prefs.UserPrefs.get_root()
        if prefs_root:
            setstudio(prefs_root)
        else:
            raise WorkspaceError('No show is studio. Set a studio to continue')

    environment.setEnv('show', show)
    user_prefs.UserPrefs.set_current_show(show)

    # setup the show specific enviornment variables
    environment.setEnv('show_path', os.path.join(environment.getEnv('shows_path'), environment.getEnv('show')))
    environment.setEnv('rel_path', os.path.join(environment.getEnv('show_path'), 'rel'))
    environment.setEnv('work_path', os.path.join(environment.getEnv('show_path'), 'work'))
    environment.setEnv('elm_work_path', os.path.join(environment.getEnv('work_path'), 'elements'))
    environment.setEnv('seq_work_path', os.path.join(environment.getEnv('work_path'), 'sequences'))
    environment.setEnv('elm_rel_path', os.path.join(environment.getEnv('rel_path'), 'elements'))
    environment.setEnv('seq_rel_path', os.path.join(environment.getEnv('rel_path'), 'sequences'))

    return environment.getEnv('show_path')


def initenv(silent=False):
    """
    initalize our enviornment from out userprefs.
    :return:ls
    """
    # set the show enviornment variables
    if not environment.getEnv('show'):
        show = user_prefs.UserPrefs.get_currentShow()
        if show:
            setshow(show)
        else:
            if not silent:
                raise WorkspaceError('No show is set. Set a show to continue')


# STUDIO
def mkstudio(studio, path):
    """
    This function creates a new studio
    :param studio: name of the studio to create
    :type studio: str
    :param path: path to create a studio at.
    :return:
    """
    path = os.path.realpath(path)
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

    setstudio(studio_path)
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


# SHOW
def mkshow(show, elementTypes=None, sequenceTypes=None):
    """
    Make a new show. This will also set the active show to the new show.
    :param show: name of the show to remove. This will be all uppercased
    :param elementTypes:
    :param sequenceTypes:
    :return: show elm
    """
    show_path = osutil.clean_path(os.path.join(environment.getEnv('shows_path'), show.upper()))
    if os.path.exists(show_path):
        raise UserError('show already exists: {}'.format(show))

    # check out the name of the element
    show = re.sub("[^A-Za-z0-9_{}]", "", str(show)).upper()
    os.mkdir(show_path)
    # set the show to re-initialize the enviornment
    user_prefs.UserPrefs.set_current_show(show)
    setshow(show)

    # tag the folder as a show
    pipeutils.addEntityTag(show_path, 'show')

    # add the show to the studio data
    studio_entity = sas_pipe.entities.studio.Studio(environment.getEnv('root'))
    studio_entity.add_show(show)

    # create a manifest file
    show_entity = sas_pipe.entities.show.Show(show_path)
    if elementTypes:
        show_entity.set_elementTypes(elementTypes)
    if sequenceTypes:
        show_entity.set_sequenceTypes(sequenceTypes)

    for type in show_entity._data['element_types']:
        os.makedirs(os.path.join(environment.getEnv('elm_work_path'), type))
        os.makedirs(os.path.join(environment.getEnv('elm_rel_path'), type))

    for type in show_entity._data['sequence_types']:
        os.makedirs(os.path.join(environment.getEnv('seq_work_path'), type))
        os.makedirs(os.path.join(environment.getEnv('seq_rel_path'), type))
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


def lsshow():
    """
    list all shows in the studio
    :return:
    """
    studio_entity = sas_pipe.entities.studio.Studio(environment.getEnv('root'))
    return studio_entity._data['shows']


# ELEMENT
def mkelm(element, type, var_data=None):
    """
    Make a new elm
    :param element: name of element to create
    :param type: type of element
    :param var_data: Optional - dictionary of variant data.
                    ex {'base' : {'mod': 'mod', 'rig': 'rig', 'tex': 'look/tex', 'mat' : 'look/mat'}}
    :return: elm entity
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))

    if type not in show_entity.elementTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.elementTypes))

    # clean the name of the element before we create stuff
    element = re.sub("[^A-Za-z0-9_{}]", "", str(element))
    elm_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path'), type, element))
    elm_rel_path = osutil.clean_path(os.path.join(environment.getEnv('elm_rel_path'), type, element))

    # setup the element
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


def rmelm(element, type):
    """
    Remove an elm
    :param element: name of element to delete
    :param type: type of element
    """
    elm_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path'), type, element))
    elm_rel_path = osutil.clean_path(os.path.join(environment.getEnv('elm_rel_path'), type, element))

    if sas_pipe.entities.element.isElement(elm_work_path) and sas_pipe.entities.element.isElement(elm_rel_path):
        shutil.rmtree(elm_work_path)
        shutil.rmtree(elm_rel_path)


def nelm(element, type=None):
    """
    Navigate to an  element work directory
    :param element: Name of the element to navigate to
    :param type: Optional- provide a specific type
    :return: element work directory
    """
    return nav(element, entityType='elm', work=True, type=type)


def nrelm(element, type=None):
    """
     Navigate to an element release directory
    :param element: Name of the element to navigate to
    :param type: Optional- provide a specific type
    :return: element release directory
    """
    return nav(element, entityType='elm', work=False, type=type)


def lselm(types=None):
    """
    List elmeents
    :return: dict of elment types and elments within the type
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    elm_work_path = osutil.clean_path(os.path.join(environment.getEnv('elm_work_path')))
    elm_dict = dict()
    types = show_entity.get_assetTypes() if not types else common.toList(types)
    for type in types:
        type_elmenets = list()
        contents = osutil.get_contents(os.path.join(elm_work_path, type))
        for content in contents:
            elm_path = os.path.join(elm_work_path, type, content)
            if sas_pipe.entities.element.isElement(elm_path):
                elm = sas_pipe.entities.element.Element(elm_path)
                type_elmenets.append(elm.name)
        elm_dict[type] = sorted(type_elmenets)
    return elm_dict


# SHOT
def mkshot(seq, shot, type=None, var_data=None):
    """
    Create a new shot
    :param seq: name of the sequence
    :param shot: name of the shot
    :param type: type of shot to create
    :param var_data: Optional - dictionary of variant data.
    :return: shot entity
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    if type is None: type = 'seq'
    if type not in show_entity.sequenceTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.sequenceTypes))

    shot_work_path = osutil.clean_path(os.path.join(environment.getEnv('seq_work_path'), type, seq, shot))
    shot_rel_path = osutil.clean_path(os.path.join(environment.getEnv('seq_rel_path'), type, seq, shot))

    # setup the element
    os.makedirs(shot_work_path)
    os.makedirs(shot_rel_path)

    # Tag the folder as a show
    pipeutils.addEntityTag(shot_work_path, 'shot')
    pipeutils.addEntityTag(shot_rel_path, 'shot')

    shot_entity = sas_pipe.entities.shot.Shot(shot_work_path)

    # if we pass var_data then add that to the elm_entity
    if var_data:
        elm_entity.set_tasks(var_data.keys())
        elm_entity.set_variants(var_data)

    variant_data = shot_entity.get_variant_tasks('base')
    for task in shot_entity.get_tasks():
        os.makedirs(os.path.join(shot_entity.work_path, variant_data[task]))
        os.makedirs(os.path.join(shot_entity.rel_path, variant_data[task]))

    return shot_entity


def rmshot(seq, shot, type=None):
    """
    Remove a shot
    :param seq: name of the sequence
    :param shot: name of the shot
    :param type: type of shot to create
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    if type is None: type = 'seq'
    if type not in show_entity.sequenceTypes:
        raise KeyError("{} is not a valid type. Types are: {}".format(type, show_entity.sequenceTypes))

    shot_work_path = osutil.clean_path(os.path.join(environment.getEnv('seq_work_path'), type, seq, shot))
    shot_rel_path = osutil.clean_path(os.path.join(environment.getEnv('seq_rel_path'), type, seq, shot))

    print shot_work_path, shot_rel_path

    if sas_pipe.entities.shot.isShot(shot_work_path) and sas_pipe.entities.shot.isShot(shot_rel_path):
        shutil.rmtree(shot_work_path)
        shutil.rmtree(shot_rel_path)


def nshot(seq, shot, type=None):
    """
    Navigate to a shot work directory
    :param seq: name of the sequence
    :param shot: name of the shot
    :param type: Optional- provide a specific type
    :return: shot work directory
    """
    code = '/'.join([seq, shot])
    return nav(code, entityType='shot', work=True, type=type)


def nrshot(seq, shot, type=None):
    """
    Navigate to a relase shot directory
    :param seq: name of the sequence
    :param shot: name of the shot
    :param type: Optional- provide a specific type
    :return: relase shot directory
    """
    code = '/'.join([seq, shot])
    return nav(code, entityType='shot', work=False, type=type)


def lsshot(types=None):
    """
    List elmeents
    :return: dict of elment types and elments within the type
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))
    seq_work_path = osutil.clean_path(os.path.join(environment.getEnv('seq_work_path')))
    shot_dict = dict()
    types = show_entity.get_sequenceTypes() if not types else common.toList(types)
    for type in types:
        type_dict = list()
        sequences = osutil.get_contents(os.path.join(seq_work_path, type))
        for seq in sequences:
            seq_path = os.path.join(seq_work_path, type, seq)
            shots = osutil.get_contents(seq_path)
            for shot in shots:
                if sas_pipe.entities.shot.isShot(os.path.join(seq_path, shot)):
                    shot = sas_pipe.entities.shot.Shot(os.path.join(seq_path, shot))
                    type_dict.append(shot.name)
        shot_dict[type] = sorted(type_dict)
    return shot_dict


def nav(code, entityType='elm', work=True, type=None):
    """
    Navigate to an element
    :param code: name of the element to find. for shots use '010/0010'
    :param entityType: type of element. Valid values are 'elm' or 'shot'
    :param work: specify if the file is a work of release file
    :param type: Optional- provide a specific type to speed up the opperation.
    :return:
    """
    show_entity = sas_pipe.entities.show.Show(environment.getEnv('show_path'))

    types = show_entity.elementTypes if entityType is 'elm' else show_entity.sequenceTypes
    if work:
        env_path = environment.getEnv('elm_work_path') if entityType is 'elm' else environment.getEnv('seq_work_path')
    else:
        env_path = environment.getEnv('elm_rel_path') if entityType is 'elm' else environment.getEnv('seq_rel_path')

    if type:
        elm_path = osutil.clean_path((os.path.join(env_path, type, code)))
        if entityType == 'elm':
            if sas_pipe.entities.element.isElement(elm_path):
                return elm_path
        else:
            if sas_pipe.entities.shot.isShot(elm_path):
                return elm_path
    else:
        for type in types:
            elm_path = osutil.clean_path((os.path.join(env_path, type, code)))
            if entityType == 'elm':
                if sas_pipe.entities.element.isElement(elm_path):
                    return elm_path
        else:
            if sas_pipe.entities.shot.isShot(elm_path):
                return elm_path


if __name__ == '__main__':
    import json

    #
    # setstudio('/Users/masonsmigel/Documents/jobs/animAide/pipeline/projects_root/testStudio')
    setshow('TEST')
    initenv()

    rmshow('demo')
