"""
@file Gun.py
@author Ryan Missel

Class that handles generating and holding the state of a Gun.
Takes in user-input on gun type, gun guild, and item level - if provided.

Unless a gun type is input, then the gun table is only rolled through Gun Table 1-6 on Pg. 81.
"""
from random import randint
from json_reader import get_file_data


class Gun:
    def __init__(self, item_level=None, gun_type=None, gun_guild=None, gun_rarity=None):
        """
        Handles generating a gun completely from scratch with no user input
        TODO: add user-input modifying the control patch
        """
        # If item level is to be generated
        if item_level in ["random", None]:
            item_level = self.get_random_ilevel()

        # Get relevant portion of the gun table based on the roll
        roll_type = str(randint(1, 6))
        roll_guild = str(randint(1, 6))
        gun_table = get_file_data("guns/gun_table.json").get(roll_type)

        # Get gun type and gun guild
        self.type = gun_table.get("type")
        self.item_level = item_level

        self.guild = gun_table.get("guild").get(roll_guild)
        self.guild_table = get_file_data("guns/guild_table.json").get(self.guild)
        self.guild_element_roll = self.guild_table.get("element_roll")

        # Get gun stats table
        self.stats = get_file_data("guns/" + self.type + ".json").get(item_level)
        self.accuracy = self.stats['accuracy']
        self.range = self.stats['range']
        self.damage = self.stats['damage']

        # Roll for gun rarity
        roll_row = str(randint(1, 4))
        roll_col = str(randint(1, 6))
        self.rarity = get_file_data("guns/rarity_table.json").get(str(roll_row)).get(roll_col)

        # Check if it was an elemental roll and if it can have an element based on guild type
        self.rarity_element_roll = False
        if type(self.rarity) is list:
            self.rarity_element_roll = True
            self.rarity = self.rarity[0]

        # Get guild information
        self.guild_mod = self.guild_table.get("tiers").get(self.rarity)
        self.guild_info = self.guild_table.get("gun_info")

        # Roll for element iff it has an appropriate guild and rarity
        # TODO - make sure malefactor ALWAYS gets an element via rounded up to lowest
        self.element = None
        if self.guild_element_roll is True and self.rarity_element_roll is True:
            roll_element = str(randint(1, 100))
            roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

            element_table = get_file_data("elements/elemental_table.json")
            self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # If the gun is Malefactor guild and it does not have an element yet, keep rolling until an element is picked
        if self.guild == "malefactor" and self.element is None:
            while self.element is None:
                roll_element = str(randint(1, 100))
                roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

                element_table = get_file_data("elements/elemental_table.json")
                self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # Get element info if it exists
        self.element_info = None
        if self.element is not None:
            if type(self.element) == list:
                self.element_info = [
                    get_file_data("elements/elemental_type.json").get(self.element[0]),
                    get_file_data("elements/elemental_type.json").get(self.element[1])
                ]
            else:
                self.element_info = get_file_data("elements/elemental_type.json").get(self.element)

        # TODO: add rolling for prefixes and red text on weapons
        self.prefix = None
        self.red_text = None

    def get_random_ilevel(self):
        """ Handles rolling for a random item level and giving back the tier key for it """
        roll_level = randint(1, 30)

        tier = None
        for key in get_file_data("guns/pistol.json").keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll_level <= upper:
                tier = key

        return tier

    def check_element_boost(self, roll, guild, rarity):
        """
        Malefactor weapons get a boost to their element roll on the table.
        Checks if the given rolled gun gets that treatment.
        :param roll: given base element roll
        :param guild: guild to check if its malefactor
        :param rarity: rarity of the gun
        :return: roll with modified cost if its malefactor and rare enough
        """
        roll = int(roll)

        if rarity == "rare" and guild == "malefactor":
            roll = roll + int(roll * 0.10)
        elif rarity == "epic" and guild == "malefactor":
            roll = roll + int(roll * 0.15)
        elif rarity == "legendary" and guild == "malefactor":
            roll = roll + int(roll * 0.20)

        roll = min(roll, 100)
        return str(roll)

    def get_element_tier(self, roll, element_table):
        """
        Handles getting the tier in which the element roll resides.
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-100 random roll
        :param element_table: loaded in dictionary of elemental_table.json
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in element_table.keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll <= upper:
                tier = key

        return tier


if __name__ == '__main__':

    types = []
    guilds = []
    item_level = []
    rarities = []

    elements = []

    for _ in range(20000):
        gun = Gun(None, None, None, None)

        if gun.guild == "malefactor" and gun.element is not None:
            elements.append(1)
        elif gun.guild == "malefactor" and gun.element is None:
            elements.append(0)

        types.append(gun.type)
        guilds.append(gun.guild)
        item_level.append(gun.item_level)
        rarities.append(gun.rarity)

    import numpy as np
    print(np.unique(types, return_counts=True))
    print(np.unique(guilds, return_counts=True))
    print(np.unique(item_level, return_counts=True))
    print(np.unique(rarities, return_counts=True))

    print("-")
    print(np.unique(elements, return_counts=True))
    exit(0)

    print("Type:", gun.type)
    print("Guild:", gun.guild)
    print("Rarity:", gun.rarity)
    print("Item Level:", gun.item_level)
    print("")
    print("Damage:", gun.damage)
    print("Range:", gun.range)
    print("Accuracy:", gun.accuracy)
    print("")
    print("Guild Mod:", gun.guild_mod)
    print("Guild Info:\n{}".format(gun.guild_info))
    print("")
    print("Element Guild Check:  ", gun.rarity_element_roll)
    print("Element Rarity Check: ", gun.guild_element_roll)
    print("Element type:         ", gun.element)
    print("Element info:\n{}".format(gun.element_info))