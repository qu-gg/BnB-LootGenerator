"""
@file json_reader.py
@author Ryan Missel

Provides json file from the resources directory
"""
import json


def get_file_data(path):
    """
    Parses the filename given, grabs the corresponding .json file, and converts it into a
    Python-usable dictionary
    :param filename: The name of the file to get
    :return: Dictionary of the converted .json file
    """
    with open(path) as f:
        data = json.load(f)

    return data