# Change Log 
When updating the changelog you must also increase the version in the `scripts/__init.py` 
file and the  `plug-ins/sasPipe_maya.py` file. 

## 2.0.4

### Added: 
* Added open publish button to the browser UI 

### Changed: 
* Changed the maya browser to filter only maya files in the content lists. 

## 2.0.3

Updated the publish and browser UI

### Added: 
* Option to keep multiple studios in memory. when a new studio is set that does not exists in 
the list its added to the ‘rootsList’ in the preferences. 
You can retrieve a list of all studios through `cmds.getstudios()'

### Changed: 
* Change the the publish ui to attempt to auto populate the publish path. Also update the guessed path whenever 
the scene changes. 
* Changed the studio selection to a combo box so the user can switch between studios.


## 2.0.2

Updated the SAS_pipeline Menu

### Added: 
* Save File menu Item to Rigging Menu 
* Implemented setStudio Menu Item
* Fixed a bug with the capture behavior of the thumbnail

### Removed: 
* Production Menu. It was redudent since the same functionality exists inside the assetBrowser

## 2.0.1

Updated the SAS_pipeline Menu

### Added: 
* More modular system for building menus. Each department has a module, they can add
more commands to their menu by editing the `menu.py` file within the module. 
 
### Changed: 
* The name of the menu to SAS instead of SAS pipeline to acount for the
more general uses. 
 


## 2.0.0

initial start of the change log

### Added: 
* First version of the pipeline
 
### Changed: 

### Removed: 
 