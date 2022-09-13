# Path Constants
# Paths are relative to the root of the project.
current_path = __file__.replace('\\', '/')
ICONS_PATH = '/'.join(current_path.split('/')[0:-3]) + '/icons'
PLUGIN_PATH = '/'.join(current_path.split('/')[0:-3]) + '/plug-ins'
SCRIPTS_PATH = '/'.join(current_path.split('/')[0:-3]) + '/scripts'
PUBLISHSTEPS_PATH = '/'.join(current_path.split('/')[0:-3]) + '/scripts/sas_pipe/maya/publish'

# Template paths
ELEMENT_TEMPLATE = "/".join(current_path.split('/')[0:-3]) + '/scripts/sas_pipe/entities/element.json'
SHOT_TEMPLATE = "/".join(current_path.split('/')[0:-3]) + '/scripts/sas_pipe/entities/shot.json'


# Maya module paths
SHOWS_PATH = 'shows'
SANDBOX_PATH = 'sandbox'
CURRENTSHOW_PATH = SHOWS_PATH + '/{currentShow}'
REL_TOKEN = 'publish'
VER_TOKEN = 'publish/versions'
WORK_TOKEN = 'work'

# Project defaults
ASSET_TYPES = ['char', 'prop', 'envi', 'envi/parts', 'temp']  # Asset types
SEQUENCE_TYPES = ['mrkt', 'seq']  # Sequence Type
# ASSET_DEPTS = ['mod', 'rig', 'look', 'art']  # Asset Departments
# SHOT_DEPTS = ['audio', 'lay', 'anim', 'crowd', 'fx', 'cfx', 'lgt', 'comp', 'mocap']  # Shot Departments
# OTHER_DEPTS = ['core']  # Other Departments
# DEPTS = ASSET_DEPTS + SHOT_TASKS + OTHER_DEPTS
SEQ_PADDING = 2
SHOT_PADDING = 3

# File type constants
DATATYPES = ['Studio', 'Show', 'Seq', 'Shot', 'Element']

MAYA_FILE_TYPE = 'ma'
