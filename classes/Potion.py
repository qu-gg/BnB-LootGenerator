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

        # Hard coded ranges that tina potions are in and the bonus to the roll
        self.tina_ranges = {
            "01-05": 0,
            "26-30": 3,
            "51-55": 5,
            "76-80": 10
        }

        # Grab a random potion id if none specified
        if potion_id == "Random":
            key = choice(list(potion_data.keys()))
            potion_id = key
            potion_dict = potion_data.get(key)
        # Otherwise, just get the key
        else:
            potion_dict = potion_data.get(potion_id)

        # Set the attributes
        self.potion_id = potion_id
        self.name = potion_dict['name']
        self.effect = potion_dict['info']
        self.cost = potion_dict['cost']
        self.tina_potion = False

        # Check id for tina range
        tina_roll = self.check_tina_range(potion_id)
        if tina_roll is not None:
            tina_dict = tina_potion_data.get(str(tina_roll))
            self.name = tina_dict['name']
            self.effect = tina_dict['info']
            self.tina_potion = True

    def check_tina_range(self, potion_id):
        """
        Check whether the given potion_id is a tina potion and then perform the tiny table roll if so
        :param potion_id: potion %
        :return: None if not a Tina Potion otherwise int relating to the potion
        """
        # Check the ID in the range
        roll_bonus = self.tina_ranges.get(potion_id, None)

        # If it isn't in the range, return None
        if roll_bonus is None:
            return None

        # Perform the roll and add the bonus, capping the roll at 30 if it goes over
        bombass_roll = randint(1, 30) + roll_bonus
        bombass_roll = min(bombass_roll, 30)
        return bombass_roll
