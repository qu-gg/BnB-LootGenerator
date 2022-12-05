"""
@file Grenade.py
@author Ryan Missel

Class that handles generating and holding the state of a Grenade.
Takes in user-input on Grenade Type, Rarity, etc - if provided.
"""
from random import choice, randint
from classes.json_reader import get_file_data


class Grenade:
    def __init__(self, base_dir, grenade_images,
                 name='', guild="Random", tier="Random",
                 grenade_type="", damage="", effect="", art_path=None):
        """ Handles generating a grenade, modified to specifics by user info """
        # Load in grenade data
        grenade_data = get_file_data(base_dir + 'resources/misc/grenades/grenade.json')
        grenade_guild = get_file_data(base_dir + 'resources/misc/grenades/grenade_guild.json')
        grenade_names = get_file_data(base_dir + 'resources/misc/grenades/grenade_lexicon.json')

        # Grab a grenade name if not given
        self.name = name if name != '' else grenade_names.get(choice(list(grenade_names.keys())))

        # Roll for a guild if not given
        if guild == "Random":
            roll = str(randint(1, 8))
            self.guild = grenade_guild.get(roll)
        else:
            self.guild = guild

        # Get the guild's tiers
        grenade_data = grenade_data.get(self.guild)

        # Roll for a tier if not given
        if tier == "Random":
            roll = str(randint(1, 5))
            self.tier = roll
        else:
            self.tier = tier

        # Get the grenade information based on tier
        grenade_dict = grenade_data.get(self.tier)

        # Grenade Damage
        self.damage = damage if damage != "" else grenade_dict.get("damage")

        # Grenade type
        self.type = grenade_type if grenade_type != "" else grenade_dict.get("type")

        # Effect
        self.effect = effect if effect != "" else grenade_dict.get("effect")

        # For Malefactor grenades that have the default effect, replace the damage type to a random element
        if self.guild == "Malefactor" and effect == "":
            elements = list(get_file_data('resources/elements/elemental_type.json').keys())
            self.effect = self.effect.replace("xx", choice(elements).title())

        # Set file art path; sample if not given
        self.art_path = ""
        if art_path not in ["", None]:
            self.art_path = art_path
        else:
            self.art_path = grenade_images.sample_grenade_image()
