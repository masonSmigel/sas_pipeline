# sas_pipeline
SCAD Animation Studios Pipeline Tools 2.0


- NOTE: V2.0.0 is currently in progress. This is a ground up redesign of the tool to add more flexiblity

# Installation
Instructions to install SAS Pipeline. 
NOTE: an easier install is coming!! This is still a WIP. 
1. Open a terminal and add `./scripts` path to your PYTHONPATH variable and `./bin` path to the PATH variable. 
    - you can add these perminately by adding the following lines to your `./bashrc` or `./zshrc` files:
         ```
         export PYTHONPATH="path/to/package/sas_pipeline/scripts:$PYTHONPATH"
         export PATH="path/to/package/sas_pipeline/bin:$PATH"
        ```
2. you can now run pipeline commands from terminal. 

# Usage
1. with the `./scripts` and `./bin` in your system you can run SAS pipeline commands. 


# Commands 
command line commands are designed for high level management of the project. This includes things like creating new
entities, seting your workspace and removing entities. 

NOTE: use the help flag in the command line for full docmentaion

`setstudio`: sets the current active studio

`setshow`: sets the current active show

`mkstudio`: creates a new studio

`mkshow`: creates a new show

`mkelm`: create a new element

`mkshot`: create a new shot 

`rmelm`: removes an element

`rmshot`: removes a shot 

`rmshow`: removes a show

`nelm`: navigate to the working directory of an element

`nrelm`: navigate to the release directory of an element

`nshot`: navigate to the working directory of a shot 

`nrshot`: navigate to the release directory of a shot 

`lsshow`: list all shows availble in the studio 

`lselm`: list all elements availble in the current show 

`lsshot`: list all shots availble in the current show 



# Philosophy
SAS pipeline is built of different entities, studios, shows, elements, and shots. 
Each entitiy contains a .manifest file with holds and manages data about that entity, and a hidden file to tag the 
directory as an entity. 

Each entity and the tasks it performs are completely software agnostic, it can then be wrapped into more complex
situations specific to each DCC. 







