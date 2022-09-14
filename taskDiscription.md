# Task Template discriptions 
This document is meant to serve as an explaination of the different tasks available in the included task templates


## Elements
Elements are any non-time based aspects of the film. This typically includes the characters, props, and enviornments. 


- `actor-anim` - The `actor-anim` is a proceduraly generate scene that 
merges the most up to date `mod-deliver`, `look-deliver` and `rig-deliver`. This package is built for animation and maya. 

- `actor-ue` -  The `actor-anim` is a proceduraly generate scene that 
merges the most up to date `mod-deliver`, `look-deliver` and `rig-deliver`. This package is built for unreal Engine. 

- `art` - This task stores any art assets needed for the artists. This can include expression sheets, turn arounds 
or any other lookdevelopment. 

- `mod-proxy` - This task is for the proxy model used in previs or other early development. 

- `mod-base` - This task is the main working file for modelling work. 

- `mod-sculpt` -  This task is used for holding zbrush sculpt files or other highres modelling files. 

- `mod-deliver` - This task if the final output of the modelling department. It is ingested into the `rig-body` and `rig-facial`.

- `mod-assemble` - This task is used for enviornments to assemble the final enviornment with the individual parts.

- `rig-proxy` - This task is used for the proxy rig used in early development. It ingests the `mod-proxy` file.   

- `rig-body` - This task is the primary task for rigging. On characters it is used for body rigs, with other 
rigs it is the primary working file. 

- `rig-facial` -  This task is available on characters for the facial rigging. 

- `rig-deliver` - This task is the final output of the rigging department. It combines the `rig-body` and `rig-facial`. 

- `look-uv` - This task is used for creating the UVs. it is used down the line for the `look-texture` and `look-surface`. 

- `look-texture` - This task is used for the texturing, primarily Substance files. 

- `look-surface` - This task is used for developing the surfacing of an element in the primary DCC. 

- `look-deliver` - This is the final output of the look department it combines the `look-uv`, `look-texture`, `look-surface`. 

## Shots
Shots are any time based media. This will be any clips that make up the final film or other time based media. 

- `anim_main` -  This task is used for the main animation elements. This will mostly be the characters. 

- `anim_mocap` - This task is used for any mocap related files used in the shot.

- `anim_lay` - This task is used for animation layout. This should be the first step in the animaiton pipeline and is used
to lock camera angles. 

- `anim_crowd` - This task is used to store any crowd animation. 

- `art` - This task is used for the art related to the shot. This can range from storyboards to artist thumbnails. 

- `reference` - This task is used to store any  reference filmed by the animator.

- `audio` - This task is used for any audio clips used in the shot.

- `cfx_crowd` - This task is used for any character fx used in the crowd elments. 

- `cfx_main` - This task is used for any character fx on main animation elements. 

- `light` - This task is used for lighting the animation shots.  

- `comp` - This task is used for compositing the final shots. 





