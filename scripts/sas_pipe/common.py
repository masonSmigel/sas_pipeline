# coding=utf-8
"""
This module contains functions common to all modules and constants
"""
from collections import OrderedDict

def toList(values):
    """
    Converts values into a items
    :param values: values to convert into a items
    :return: items of values
    """
    if not isinstance(values, (list, tuple)):
        values = [values]
    return values


def getFirstIndex(var):
    """
    Return the first index of a items
    :param var: items to get index from
    :type var: list | tuple
    :return: first index of a items or tuple
    """
    if isinstance(var, (list, tuple)):
        if not len(var):
            return var
        return var[0]
    else:
        return var


def convertDictKeys(dictionary):
    """
    Converts Dictionary keys from unicodes to strings

    :param dictionary: the ditionary you want to convert the eyes on
    :type dictionary: dict

    :return: The dictionary with its keys converted
    :rtype: dict
    """

    # If its not a dictionary return it.
    if not isinstance(dictionary, dict):
        return dictionary

    # If its a dictionary look through the keys/values and convert them
    return OrderedDict((str(k), convertDictKeys(v)) for k, v in dictionary.items())


def tryIndex(list, index):
    try:
        return list[index]
    except IndexError:
        return None
