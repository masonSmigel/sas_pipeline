"""Build sas_pipe pipeline menu"""

import maya.cmds as cmds

import sas_pipe.maya.ui.widgets.menuBase as menuBase


def show_set_show(*args):
    import sas_pipe.maya.ui.set_show_ui as set_show_ui
    reload(set_show_ui)
    set_show_ui.SetShowUI.show_dialog()


def show_add_show(*args):
    import sas_pipe.maya.ui.add_show_ui as add_show_ui
    add_show_ui.AddShowUI.show_dialog()


def show_add_asset(*args):
    import sas_pipe.maya.ui.add_asset_ui as add_asset_ui
    # reload(add_asset_ui)
    add_asset_ui.AddAssetUI.show_dialog()


def show_add_sequence(*args):
    import sas_pipe.maya.ui.add_sequence_ui as add_sequence_ui
    # reload(add_sequence_ui)
    add_sequence_ui.AddSeqUi.show_dialog()


def show_add_shot(*args):
    import sas_pipe.maya.ui.add_shot_ui as add_shot_ui
    # reload(add_shot_ui)
    add_shot_ui.AddShotUI.show_dialog()


def show_open_asset(*args):
    import sas_pipe.maya.ui.open_asset_ui as open_asset_ui
    # reload(open_asset_ui)
    open_asset_ui.OpenAssetUi.show_dialog()


def show_open_shot(*args):
    import sas_pipe.maya.ui.open_shot_ui as open_shot_ui
    # reload(open_shot_ui)
    open_shot_ui.OpenShotUi.show_dialog()


def save_version(*args):
    import sas_pipe.maya.ui.save_version_ui as save_version_ui
    reload(save_version_ui)
    save_version_ui.SaveVersionUi.show_dialog()


def quick_save(*args):
    import sas_pipe.maya.ui.quicksave as quicksave
    reload(quicksave)
    quicksave.QuickSave()


def publish(*args):
    import sas_pipe.maya.ui.publish_entity as publish_entity
    # reload(publish_entity)
    publish_entity.PublishEntityUi.show_dialog()


def import_file(*args):
    import sas_pipe.maya.ui.import_asset as import_asset
    # reload(import_asset)
    import_asset.ImportAssetUi.show_dialog()


def reference_file(*args):
    import sas_pipe.maya.ui.reference_asset as reference_asset
    # reload(reference_asset)
    reference_asset.ReferenceAssetUi.show_dialog()


def check_root_path(*args):
    import sas_pipe.maya.maya_manager as maya_pipeline
    maya_pipeline.MayaManager.validate_root(log=True)


def set_root_path(*args):
    import sas_pipe.maya.ui.set_root as set_root
    reload(set_root)
    set_root.run()


def about(*args):
    import sas_pipe.maya.ui.about_ui as about_ui
    about_ui.AboutUi.show_dialog()


class SASMenu(menuBase._menu):
    def build(self):
        self.addMenuItem(label='Curent Show:', en=False)
        self.addMenuItem(label='Set Show', command=show_set_show)
        self.addMenuItem(label='Add Show', command=show_add_show)
        self.addDivider()
        # create = self.addSubMenu(label='Add')
        create = None
        self.addMenuItem(label='Add Asset', parent=create, command=show_add_asset)
        self.addMenuItem(label='Add Sequence', parent=create, command=show_add_sequence)
        self.addMenuItem(label='Add Shot', parent=create, command=show_add_shot)
        # self.addMenuItem(label='Insert Sequence', parent=create)
        # self.addMenuItem(label='Insert Shot', parent=create)
        self.addDivider()
        self.addMenuItem(label='Open Asset', command=show_open_asset)
        self.addMenuItem(label='Open Shot', command=show_open_shot)
        self.addDivider()
        self.addMenuItem(label='Save Version', command=save_version)
        self.addMenuItem(label='Quick Save', command=quick_save)
        self.addMenuItem(label='Publish', command=publish)
        self.addDivider()
        self.addMenuItem(label='Reference Asset', command=reference_file)
        self.addMenuItem(label='Import Asset', command=import_file)
        self.addDivider()
        advanced = self.addSubMenu(label='Advanced...', tearOff=False)
        self.addMenuItem(label='Check Root Path', parent=advanced, command=check_root_path)
        self.addMenuItem(label='Set Root Path', parent=advanced, command=set_root_path)
        self.addMenuItem(label='About', command=about)

    @staticmethod
    def display_mayaMenu(show_name):
        try:
            items = cmds.menu('SASPipelineMenu', q=True, ia=True)
            if len(items) > 0:
                cmds.menuItem(items[0], e=True, l='Current Show: {}'.format(show_name))
        except:
            pass
