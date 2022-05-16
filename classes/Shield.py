"""
@file Shield.py
@author Ryan Missel

Class that handles generating and holding the state of a Shield.
Takes in user-input on Shield Type, Rarity, etc - if provided.
"""
from random import choice, randint
from classes.json_reader import get_file_data


class Shield:
    def __init__(self, base_dir, name='', guild="Random", tier="Random", capacity="", recharge="", effect=""):
        """ Handles generating a shield, modified to specifics by user info """
        # Load in shield data
        shield_data = get_file_data(base_dir + 'resources/misc/shields/shield.json')
        shield_guild = get_file_data(base_dir + 'resources/misc/shields/shield_guild.json')
        shield_names = get_file_data(base_dir + 'resources/misc/shields/shield_lexicon.json')

        # Grab a shield name if not given
        self.name = name if name != '' else shield_names.get(choice(list(shield_names.keys())))

        # Roll for a guild if not given
        if guild == "Random":
            roll = str(randint(1, 8))
            self.guild = shield_guild.get(roll)
        else:
            self.guild = guild

        # Get the guild's tiers
        shield_data = shield_data.get(self.guild)

        # Roll for a tier if not given
        if tier == "Random":
            roll = str(randint(1, 5))
            self.tier = roll
        else:
            self.tier = tier

        # Get the shield information based on tier
        shield_dict = shield_data.get(self.tier)

        # Capacity
        self.capacity = capacity if capacity != "" else shield_dict.get("capacity")

        # Recharge
        self.recharge = recharge if recharge != "" else shield_dict.get("recharge")

        # Effect
        self.effect = effect if effect != "" else shield_dict.get("effect")
