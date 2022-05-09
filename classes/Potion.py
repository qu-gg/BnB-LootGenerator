"""
@file Potion.py
@author Ryan Missel

Class that handles generating and holding the state of a Potion.
Takes in user-input on potion ID - if provided.
"""
from random import randint, choice
from classes.json_reader import get_file_data


class Potion:
    def __init__(self, base_dir, potion_id=None):
        """ Handles generating a potion, modified to specifics by user info """
        # Load in potion data
        potion_data = get_file_data(base_dir + 'resources/misc/potions/potion.json')
        tina_potion_data = get_file_data(base_dir + 'resources/misc/potions/tina_potion.json')

        # If potion ID is provided, just get the file data
        if potion_id is not None:
            potion_dict = potion_data.get(potion_id)
        # Otherwise, roll on the table and get it randomly
        else:
            key = choice(list(potion_data.keys()))
            potion_id = key
            potion_dict = potion_data.get(key)

        # Set the attributes
        self.potion_id = potion_id
        self.name = potion_dict['name']
        self.effect = potion_dict['info']
        self.cost = potion_dict['cost']


if __name__ == '__main__':
    potion = Potion('../')
    print()