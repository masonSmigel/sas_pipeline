# sas_pipeline
SCAD Animation Studios Pipeline Tools

# Installation
Instructions to install SAS Pipeline for maya
1. Place the sas_pipeline module somewhere you'd like to keep it. Try to keep it somewhere you'll be able to easily acess it.
    * If you dont know where to save it a good place is: `MAYA_APP_DIR/<version>/plug-ins`
2. When your folder is in place, drag the file `drag_into_maya.py` into maya.
    * This will create a `sasPipe.mod` file at the location  `MAYA_APP_DIR/modules`. 
    * File expolorer dialog will pop up asking for you to select a root folder. This is where all files associated with SAS Pipeline will be created. When working on with a team this should be a shared drive.
3. The plugin is now available. You should see a new 'SAS Pipeline' menu in maya. 
    * The shelf Icon may not appear! Dont worry it will show up the next time you open maya 
    * Open the plugin manager and select auto-load to load the menu in every new maya session


# Usage
Once the plugin is loaded a 'SAS Pipeline' menu is avaiable.
1. On the plugins initialization you must specifiy a root path. If this is skipped set a root path now user the `SAS Pipeline> Advanced...> Set Root Path`.
    * A root path must be specified to continue. It will be saved at 'sas_pipeline/userPrefs.pref'
2. Next you must specify a show. You can select a show by using `SAS Pipeline> Set Show` or create a new show `SAS Pipeline> Add Show`
3. After that all menu items are available.

# Pipeline Structure
SAS pipline will setup a project with the following structure.
```
├──root                      # Root of the studio enviornment
 ├── depts                   # Contains folders for each dept. This can be used for non-production studio work such as RnD.
 | └── anim...               # departments (auto populated when any project settings.json are updated)
 └── shows                   # Contains all shows within the studio
   ├── SHOW                  # current show
   | ├── work                # Working directory. Artist should work on files here. This directory can be messy.
   | | ├── assets            # Asset based entities. Not time based.
   | | | └── char ...        # Types of assets. (auto populated via the 'asset_types' attribute in the settings.json file)
   | | |    └── charA ...    # Asset Enitity
   | | |        └── mod ...  # Asset tasks. (auto populated via the 'asset_task' attribute in the settings.json file)
   | | └── sequences         # Sequence based entities. Time based.
   | | | ├── seq ...         # Types of sequences. (auto populated via the 'seq_types' attribute in the settings.json file)
   | | |   └── 010 ...       # Sequence Entity
   | | |     └── 0010 ...    # Shot Entity
   | | |       └── anim ...  # Shot tasks. (auto populated via the 'shot_tasks' attribute in the settings.json file)
   | ├── rel                 # Release directory. This contains all published files
   | | | └── ...             # Mirrors SHOW/work stucture.
   | └── settings.json       # Settings for the show. All settings are updated the next time sas_pipeline is run
   └── ...
 ```


# Update
Copy `sas_pipeline/plugins` and `sas_pipeline/scripts` and replace the existing sas_pipeline installation.
Restart Maya


