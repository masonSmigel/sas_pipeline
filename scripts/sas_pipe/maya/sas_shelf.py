"""Build sas_pipe pipeline menu"""

import maya.cmds as cmds

import sas_pipe.maya.ui.widgets.shelfBase as shelfBase


class SASShelf(shelfBase._shelf):

    def build(self):
        self.addButon(label='Pipe', icon='sas_x32.png', command='cmds.loadPlugin("sasPipe_maya")')


if __name__ == '__main__':
    shelf = SASShelf(name='SAS')
