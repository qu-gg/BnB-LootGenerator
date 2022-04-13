"""
@file json_reader.py
@author Ryan Missel

Provides json file from the resources directory
"""
import json
import os.path


def get_file_data(filename):
    """
    Parses the filename given, grabs the corresponding .json file, and converts it into a
    Python-usable dictionary
    :param filename: The name of the file to get
    :return: Dictionary of the converted .json file
    """
    data = None
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../resources/" + filename)
    with open(path) as f:
        data = json.load(f)

    return data