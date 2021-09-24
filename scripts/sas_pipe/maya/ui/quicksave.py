import os

import maya.cmds as cmds

import sas_pipe.maya.maya_pipe as maya_pipeline
import sas_pipe.shared.filenames as filenames


def QuickSave():
    proj = maya_pipeline.MayaPipeline()

    sceneName = os.path.basename(cmds.file(q=True, sn=True))
    path = os.path.dirname(cmds.file(q=True, sn=True))

    filename = filenames.increment_filename(sceneName)
    return proj._save_file(os.path.join(path, filename))

if __name__ == '__main__':
    filenames.increment_filename(
        "/Users/masonsmigel/Dropbox (Neko Productions)/SAS/shows/DEMO/work/assets/char/mrCube/mod/damaged",
        'mrCube_mod_v001.ma')
