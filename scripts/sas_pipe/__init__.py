VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0

version_info = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
version = '%i.%i.%i' % version_info
__version__ = version

__author__ = 'Mason Smigel'

__all__ = ['version', 'version_info', '__version__']
