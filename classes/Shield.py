"""
@file shield.py
@author Ryan Missel

Class that handles generating and holding the state of a shield.
Takes in user-input on Shield Type, Rarity, and Class - if provided.
"""
from random import choice, randint
from classes.json_reader import get_file_data


class shield:
    def __init__(self, base_dir, name='', shield_id="Random", shield_type='', rarity="Random"):
        """ Handles generating a shield, modified to specifics by user info """
        # Load in shield data
        shield_data = get_file_data(base_dir + 'resources/misc/shields/shield.json')
        shield_names = get_file_data(base_dir + 'resources/misc/shields/shield_lexicon.json')
