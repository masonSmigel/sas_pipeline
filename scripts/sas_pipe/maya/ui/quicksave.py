import os

import maya.cmds as cmds

import sas_pipe.maya.maya_manager as maya_pipeline


def QuickSave():
    proj = maya_pipeline.MayaManager()

    e = proj.get_entity_from_curent_file()
    t = proj.get_task_from_current_file()
    filename = os.path.basename(cmds.file(q=True, sn=True))
    warble = None
    if len(filename.split('.')) > 2:
        warble = filename.split('.')[1]

    return proj.save_new_version(entity=e, task=t, file_type='ma', warble=warble)
