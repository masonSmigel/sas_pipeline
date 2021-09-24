""" This module is an instance of the pipeline manager Class for maya"""
import os
from functools import wraps

import maya.cmds as cmds
import pymel.core as pm

import sas_pipe.maya.sas_menu as sas_menu
import sas_pipe.shared.common as common
import sas_pipe.shared.pipeline as pipeline
from sas_pipe.shared.entities import asset_, shot_
from sas_pipe import Logger


def block_prompt(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        # Grabs the initial value.
        prompt_val = cmds.file(prompt=True, q=True)

        try:
            cmds.file(prompt=False)
            return func(*args, **kwargs)

        finally:
            # Resets to the original value, this way you don't suddenly turn the prompt on, when someone wanted it off.
            cmds.file(prompt=prompt_val)

    return wrap


class MayaPipeline(pipeline.Pipeline):

    def __init__(self, root_path=None):
        super(MayaPipeline, self).__init__(root_path, )

        # Automatically load the last show if one is available
        if self.prefs.has_key('lastShow'):
            self.set_show(self.prefs['lastShow'])

    def get_entity_from_curent_file(self, path=None):
        """
        Get an entity object from the current file
        :return:
        """
        if not path:
            path = os.path.normpath(pm.sceneName()).replace('\\', '/')

        file_info = self.parse_path(path)

        if file_info.has_key('stage'):
            if file_info['stage'] == common.ASSETS:
                for task in common.ASSET_TASKS:
                    if task in path:
                        split_path = path.rsplit('{}{}'.format('/', task), 1)
                        return asset_.Asset(split_path[0])
            elif file_info['stage'] == common.SEQUENCES:
                for task in common.SHOT_TASKS:
                    if task in path:
                        split_path = path.rsplit('{}{}'.format('/', task), 1)
                        return shot_.Shot(split_path[0])
        else:
            return None

    def set_show(self, show):
        super(MayaPipeline, self).set_show(show)
        sas_menu.SASMenu.display_mayaMenu(show)

    def get_task_from_current_file(self, path=None):
        if not path:
            path = pm.sceneName()
        file_info = self.parse_path(path)
        if file_info.has_key('task'):
            return file_info['task']

    def _save_file(self, path):
        """
       Save a maya file
        """
        if isinstance(path, (list, tuple)):
            path = path[0]
        pm.saveAs(path)
        Logger.info("Saved file: {}".format(path))
        return path

    @block_prompt
    def _open_file(self, path):
        """
       Open a maya file
        """
        if isinstance(path, (list, tuple)):
            path = path[0]

        pm.openFile(path, prompt=False, f=True)

        # rebuild references relative to user root path
        for reference in pm.listReferences(refNodes=True):
            fileReference = reference[1]
            reference_path = os.path.normpath(fileReference.path).replace('\\', '/')

            if self.root_path not in reference_path and os.path.basename(self.root_path) in reference_path:
                if os.path.basename(self.root_path) in reference_path:
                    rel_path = reference_path.split('{}/'.format(os.path.basename(self.root_path)), 2)[-1]
                    new_ref_path = os.path.join(self.root_path, rel_path)
                    if os.path.exists(new_ref_path) and os.path.isfile(new_ref_path):
                        fileReference.load(newFile=new_ref_path)
                        Logger.info('Reference remaped from:  {} to {}'.format(reference_path, new_ref_path))
                    else:
                        Logger.warning('Failed to relocate reference for {}'.format(reference_path))
                else:
                    Logger.warning(
                        'Reference does not exist under the root:  {}'.format(os.path.basename(self.root_path)))
        self.ensure_undo_on()

    def _import_file(self, path):
        """
        Import a maya file
        """
        if isinstance(path, (list, tuple)):
            path = path[0]
        namespace = os.path.splitext(os.path.basename(path))[0]
        print namespace
        pm.importFile(path, ns=namespace)
        self.ensure_undo_on()

    def _reference_file(self, path):
        """
        Reference a maya file
        """
        if isinstance(path, (list, tuple)):
            path = path[0]
        namespace = os.path.splitext(os.path.basename(path))[0]
        pm.createReference(path, ns=namespace, gr=False)
        self.ensure_undo_on()

    @staticmethod
    def ensure_undo_on():
        if not pm.undoInfo(q=True, state=True):
            pm.undoInfo(state=True)
