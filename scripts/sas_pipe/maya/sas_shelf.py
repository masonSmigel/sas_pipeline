"""Build sas_pipe pipeline menu"""

import maya.cmds as cmds

import sas_pipe.maya.ui.widgets.shelfBase as shelfBase


class SASShelf(shelfBase._shelf):

    def build(self):
        self.addButon(label='Pipe', icon='sas_x32.png', language='mel', command='loadPlugin "sasPipe_maya";', doubleCommand='')


if __name__ == '__main__':
    shelf = SASShelf(name='SAS')
