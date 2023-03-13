"""
@file Relic.py
@author Ryan Missel

Class that handles generating and holding the state of a Relic.
Takes in user-input on Relic Type, Rarity, and Class - if provided.
"""
import shutil
import requests

from PIL import Image
from random import choice, randint
from classes.json_reader import get_file_data


class Relic:
    def __init__(self, base_dir, relic_images,
                 name='', relic_id="Random", relic_type='', rarity="Random",
                 effect='', class_id="Random", class_effect='', relic_art_path=None):
        """ Handles generating a relic, modified to specifics by user info """
        # Load in relic data
        relic_data = get_file_data(base_dir + 'resources/misc/relics/relic.json')
        relic_cost = get_file_data(base_dir + 'resources/misc/relics/relic_cost.json')
        relic_class = get_file_data(base_dir + 'resources/misc/relics/relic_class.json')
        relic_names = get_file_data(base_dir + 'resources/misc/relics/relic_lexicon.json')

        # Denotes whether relic data has been filtered or not, used in relic ID key grabbing
        filtered_flag = False

        # Filter the rarity if it is given
        if rarity != "Random" and rarity in ["Common", "Uncommon", "Rare"]:
            # Filter relic data to that class of effects
            temp = dict()
            for k, v in relic_data.items():
                if v['rarity'] == rarity:
                    temp[k] = v
            relic_data = temp
            filtered_flag = True

        # Filter the relic type if it is given and it is not a custom one
        relic_types = set([v['type'] for _, v in relic_data.items()])
        if relic_type != "Random" and relic_type in relic_types:
            temp = dict()
            for k, v in relic_data.items():
                if v['type'] == relic_type:
                    temp[k] = v
            relic_data = temp
            filtered_flag = True

        # Grab a random relic id if none specified
        if relic_id == "Random" and filtered_flag is True:
            relic_id = choice(list(relic_data.keys()))
            relic_dict = relic_data.get(relic_id)
        elif relic_id == "Random":
            relic_id = self.get_relic_tier(randint(1, 100), relic_data)
            relic_dict = relic_data.get(relic_id)
        # Otherwise, just get the key
        else:
            relic_data = get_file_data(base_dir + 'resources/misc/relics/relic.json')
            relic_dict = relic_data.get(relic_id)

        self.relic_id = relic_id

        # Relic Name
        self.name = name if name != '' else relic_names[choice(list(relic_names.keys()))]

        # Relic Type
        self.type = relic_type if relic_type != '' else relic_dict['type']

        # Relic Rarity
        self.rarity = rarity if rarity != "Random" else relic_dict['rarity']
        self.rarity = self.rarity.lower()

        # Effect
        self.effect = effect if effect != '' else relic_dict['effect']

        # Class effect
        self.class_effect = class_effect if class_effect != '' else relic_dict['class_effect']

        # Class ID (which class)
        self.class_id = class_id if class_id != "Random" else relic_class[choice(list(relic_class.keys()))]

        # Cost of relic
        self.cost = relic_cost[self.rarity]

        # Set file art path; sample if not given
        self.relic_art_path = base_dir + 'output/relics/temporary_relic_image.png'
        if relic_art_path not in ["", None]:
            try:
                try:
                    # Test URL
                    response = requests.get(relic_art_path, stream=True)
                    img = Image.open(response.raw)
                    img.save(self.relic_art_path)
                except:
                    shutil.copy(relic_art_path, self.relic_art_path)
            except:
                relic_images.sample_relic_image()
        else:
            relic_images.sample_relic_image()

    def get_relic_tier(self, roll, relic_data):
        """
        Handles getting the tier of relic in which the given roll resides
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-100 random roll
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in relic_data.keys():
            # Split key into range
            split = key.split('-')

            # Event that the roll percent is a unique number
            if len(split) == 1 and int(key) == roll:
                tier = key

            # Event that the roll percent is a range
            if len(split) == 2 and int(split[0]) <= roll <= int(split[1]):
                tier = key

        return tier
