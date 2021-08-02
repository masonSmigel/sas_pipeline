""" Naming Functions for directories"""
import os
import re
import string

import sas_pipe.shared.os_utils as dir
from sas_pipe.shared.logger import Logger

DELIMINATOR = '_'
WORK_NAMEINGTEMPLATE = '{BASE}_{TASK}_v{INDEX}.{WARBLE}.{EXTENSION}'
REL_NAMEINGTEMPLATE = '{BASE}_{TASK}.{WARBLE}.{EXTENSION}'
PADDING = 3
MAXITTERATIONS = 10
NAMETEMPLATETOKENS = ["TASK",
                      "BASE",
                      "INDEX",
                      "WARBLE",
                      "EXTENSION",
                      ]
REQUIREDTOKENS = ['TASK',
                  'BASE',
                  'EXTENSION']


def normalize(string):
    """
    Normalize a string
    :param string:
    :type string: str
    :return: a normalized string
    """
    return re.sub("[^A-Za-z0-9_{}.]", "", str(string))


def is_unique_file(file, path):
    """
    Check if name is unique
    :param file: string to test
    :type file: str

    :param path: path to search in
    :type path: str

    :return: if the name is unique
    :rtype: bool
    """
    if not os.path.isfile(os.path.join(path, file)):
        Logger.warning("Object {} does not exist.".format(file))
        return
    return False if os.path.isfile(os.path.join(path, file)) else True


def get_unique_filename(work=True, base=None, task=None, warble=None, ext=None, path=None):
    """
    Create a new name. if the name exists, increiment the index.
    :param work: use work nameing template. If fasle will use relese naming template
    :type work: bool

    :param base: entity code of the file
    :type base: str

    :param task: task of the file to save
    :type task: str

    :param warble: any string to add to an object name
    :type warble: str

    :param ext:
    :type ext: str

    :param path: path to compare generated names with
    :type path: str

    :return: Name of an object
    :rtype: str
    """
    # Check to make sure the name is unique

    index = str('1').zfill(PADDING)
    if path:
        highest_int = get_highest_index(path=path)

        if highest_int >= 1:
            index = str(highest_int + 1).zfill(PADDING)

    if work:
        name = format_name(WORK_NAMEINGTEMPLATE, base=base, task=task, warble=warble, index=index, ext=ext)
    else:
        name = format_name(REL_NAMEINGTEMPLATE, base=base, task=task, warble=warble, ext=ext)
    return name


def validate_name_template(template, valid_tokens, log=True):
    """
    validate naming template
    :param template: template to validate
    :param valid_tokens: valid tokns for the rule
    :param log:
    :return:
    """
    invalid_tokens = list()
    for token in string.Formatter().parse(template):
        if token[1] in valid_tokens:
            continue
        elif token[1] is None and token[0]:
            continue
        else:
            invalid_tokens.append(token[1])
    if invalid_tokens:
        if log:
            Logger.warning(
                '{} not valid tokens. Valid tokens are: {}'.format(invalid_tokens, NAMETEMPLATETOKENS))
        return
    else:
        return True


def format_name(template, base=None, task=None, warble=None, index=None, ext=None):
    """
    Take given arguments and formats them into the naming convention
    """

    if validate_name_template(template, valid_tokens=NAMETEMPLATETOKENS):
        if not base:
            Logger.error("Must supply  base to create a name.")
            return
        if not task:
            Logger.error("Must supply a task to create a name.")
            return
        if not warble:
            warble = ''
        if not ext:
            Logger.error("Must supply an extension to create a name.")
            return
        if not index:
            index = ''
        else:
            index = str(index).zfill(PADDING)

        name = str(template.format(BASE=base,
                                   TASK=task,
                                   WARBLE=warble,
                                   INDEX=index,
                                   EXTENSION=ext,
                                   ))

        # Look through the string and remove any double periods.
        # These may appear if a warble is not provided
        rx = re.compile(r'\.{2,}')
        name = rx.sub('.', name)

        return normalize(name)
    return


def get_highest_index(path, return_file=False):
    """
    Get the index and filename of the file with the highest index in a path
    :param path: path to seach in
    :type path: str

    :param return_file: If true returns the filename. If false returns an Int
    :type return_file: bool

    :return: filename or int(index) of the highest numbered version
    :rtype: int | str

    """
    highest_int = 1
    highest_file = None

    for index, file in enumerate(dir.get_contents(path)):
        base_name = file.split('.')[0]
        s = re.findall("\d+$", base_name)
        file_index = (int(s[0]) if s else -1)
        try:
            int_index = int(file_index)
            if int_index >= highest_int:
                highest_int = int_index
                highest_file = file
        except ValueError:
            continue

    if return_file:
        return highest_file
    return highest_int


def format_float(string, padding=2, decimal=0):
    """format the float"""
    decimal_string = '.{}f'.format(decimal)
    return normalize(format(string, decimal_string).zfill(padding + 1))
