"""
@file Melee Weapons.py
@author Ryan Missel

Class that handles generating and holding the state of a Melee Weapons.
Takes in user-input on melee type, melee guild, and item level - if provided.

Unless a melee type is input, then the melee table is only rolled through Melee Weapons Table 1-6 on Pg. 81.
"""
from random import randint, choice
from classes.json_reader import get_file_data


class MeleeWeapon:
    def __init__(self, base_dir, melee_images,
                 name=None, item_level=None, melee_guild=None, melee_rarity=None,
                 element_damage=None, rarity_element=False, selected_elements=None,
                 prefix=True, redtext_name="", redtext_info="",
                 melee_art=None):
        """ Handles generating a melee completely from scratch, modified to specifics by user info """
        # If item level is to be generated
        self.item_level = item_level
        if item_level in ["random", None]:
            self.item_level = self.get_random_ilevel(base_dir)

        # Roll for a random name
        self.name = name
        if name in ['random', None]:
            roll_name_len = randint(1, 2)
            name_table = get_file_data(base_dir + 'resources/guns/lexicon.json')
            number_names = len(name_table.keys()) - 1
            names = [name_table.get(str(randint(1, number_names))) + ' ' for _ in range(roll_name_len)]
            self.name = ''.join(names)

        # Get guild information
        self.guild_table = get_file_data(base_dir + "resources/misc/melees/guild_table.json")
        if melee_guild in ['random', None]:
            self.guild = choice(list(self.guild_table.keys()))
        else:
            self.guild = melee_guild

        self.guild_table = self.guild_table.get(self.guild)
        self.guild_element_roll = self.guild_table.get("element_roll")

        # Roll melee rarity if random
        if melee_rarity in ['random', None]:
            roll_row = str(randint(1, 4))
            roll_col = str(randint(1, 6))
            self.rarity = get_file_data(base_dir + "resources/guns/rarity_table.json").get(str(roll_row)).get(roll_col)
        # If a rarity is specified, then roll for including an element
        else:
            self.rarity = melee_rarity
            if self.check_element_odds(base_dir, self.rarity):
                self.rarity = [melee_rarity, "element"]

        # If an element roll is forced, add if not already an element
        if rarity_element is True and type(self.rarity) != list:
            self.rarity = [self.rarity, "element"]

        # Check if it was an elemental roll and if it can have an element based on guild type
        self.rarity_element_roll = False
        if type(self.rarity) is list:
            self.rarity_element_roll = True
            self.rarity = self.rarity[0]

        # Add cost information
        self.cost = get_file_data(base_dir + "resources/guns/gun_cost.json").get(self.rarity.lower())

        # Get guild information
        self.guild_mod = self.guild_table.get("tiers").get(self.rarity)

        # Element rolling and parsing
        self.element = None
        self.element_info = []
        self.element_bonus = ""

        # Roll for element iff it has an appropriate guild and rarity
        if len(selected_elements) > 0:
            self.element = selected_elements
        elif self.guild_element_roll is True and self.rarity_element_roll is True:
            roll_element = str(randint(1, 100))
            element_table = get_file_data(base_dir + "resources/elements/elemental_table.json")
            self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # Check for passed in element, overwrites any rolled damage die
        if element_damage != "":
            self.element_bonus = f"(+{element_damage})"
        # Check all element entries for a bonus die
        elif self.element is not None:
            for ele_idx, ele in enumerate(self.element):
                if '(' in ele or ')' in ele:
                    self.element_bonus = ele[ele.index('('):ele.index(')') + 1]
                    self.element[ele_idx] = ele.split(' ')[0]
        self.element_bonus = self.element_bonus.replace("(", "").replace(")", "")

        # Get element info if it exists
        if self.element is not None:
            for element in self.element:
                self.element_info.append(get_file_data(f"{base_dir}resources/elements/elemental_type.json").get(element))

        if self.element is None:
            self.element = []

        # Prefix parsing, either Random or Selected
        self.prefix_name = ""
        self.prefix_info = ""
        prefix_table = get_file_data(base_dir + "resources/misc/melees/prefix.json")
        if prefix == "Random":
            # For melee weapons, common items cannot have prefixes
            if self.rarity == "common":
                roll_prefix = 1
            else:
                roll_prefix = str(randint(1, 20))
            prefix = prefix_table.get(self.get_prefix(roll_prefix, prefix_table))
        else:
            prefix = prefix_table.get(prefix)

        # Append to the Prefix onto the weapon name
        if prefix != "None":
            self.prefix_name = prefix['name']
            self.prefix_info = prefix['info']
            self.name = self.prefix_name + ' ' + self.name
        else:
            self.name = self.name[1:]

        # Red Text assignment
        self.redtext_name = redtext_name
        self.redtext_info = redtext_info

        # Set file art path; sample if not given
        self.gun_art_path = ""
        if melee_art not in ["", None]:
            self.melee_art_path = melee_art
        else:
            self.melee_art_path = melee_images.sample_melee_image(self.guild)

    def get_random_ilevel(self, base_dir):
        """ Handles rolling for a random item level and giving back the tier key for it """
        roll_level = randint(1, 30)

        tier = None
        for key in get_file_data(base_dir + "resources/guns/gun_types.json").get("pistol").keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll_level <= upper:
                tier = key

        return tier
    def check_element_odds(self, base_dir, rarity):
        """
        If a rarity is specified, check the odds that that rarity is an elemental roll and make the check
        Only executed if the rarity is pre-specified, otherwise the full roll is rolled.
        :param base_dir: system executable base directory
        :param rarity: specified rarity
        :return: True if an element roll
        """
        elements, total = 0, 0
        for key in get_file_data(base_dir + "resources/guns/rarity_table.json").values():
            for val in key.values():
                # Check for non-element
                if type(val) == str and val == rarity:
                    total += 1
                # Check for element
                elif type(val) == list and val[0] == rarity:
                    elements += 1
                    total += 1

        element_roll = randint(1, total)
        if element_roll <= elements:
            return True
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

    def get_prefix(self, roll, prefix_table):
        """
        Handles getting the prefix in which the roll resides.
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-20 random roll
        :param prefix_table: loaded in dictionary of prefix.json
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in prefix_table.keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll <= upper:
                tier = key

        return tier
