"""
@file Gun.py
@author Ryan Missel

Class that handles generating and holding the state of a Gun.
Takes in user-input on gun type, gun guild, and item level - if provided.

Unless a gun type is input, then the gun table is only rolled through Gun Table 1-6 on Pg. 81.
"""
from random import randint
from classes.json_reader import get_file_data


class Gun:
    def __init__(self, base_dir, gun_images,
                 name=None, item_level=None, gun_type=None, gun_guild=None, gun_rarity=None,
                 damage_balance=False,
                 element_damage=None, rarity_element=False, selected_elements=None,
                 prefix=True, redtext=True,
                 gun_art=None):
        """ Handles generating a gun completely from scratch, modified to specifics by user info """
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

        # Get relevant portion of the gun table based on the roll
        if gun_type in ['random', None]:
            roll_type = str(randint(1, 6))
            gun_table = get_file_data(base_dir + "resources/guns/gun_table.json").get(roll_type)
        else:
            gun_table = get_file_data(base_dir + "resources/guns/gun_table.json").get(gun_type)

        # Get gun type
        self.type = gun_table.get("type")

        # Get guild information
        if gun_guild in ['random', None]:
            roll_guild = str(randint(1, 6))
            self.guild = gun_table.get("guild").get(roll_guild)
        else:
            self.guild = gun_guild

        self.guild_table = get_file_data(base_dir + "resources/guns/guild_table.json").get(self.guild)
        self.guild_element_roll = self.guild_table.get("element_roll")

        # Get gun stats table
        self.stats = get_file_data(base_dir + f"resources/guns/{damage_balance}.json").get(self.type).get(self.item_level)
        self.accuracy = self.stats['accuracy']
        self.range = self.stats['range']
        self.damage = self.stats['damage']

        # Roll gun rarity if random
        if gun_rarity in ['random', None]:
            roll_row = str(randint(1, 4))
            roll_col = str(randint(1, 6))
            self.rarity = get_file_data(base_dir + "resources/guns/rarity_table.json").get(str(roll_row)).get(roll_col)
        # If a rarity is specified, then roll for including an element
        else:
            self.rarity = gun_rarity
            if self.check_element_odds(base_dir, self.rarity):
                self.rarity = [gun_rarity, "element"]

        # If an element roll is forced, add if not already an element
        if rarity_element is True and type(self.rarity) != list:
            self.rarity = [self.rarity, "element"]

        # Check if it was an elemental roll and if it can have an element based on guild type
        self.rarity_element_roll = False
        if type(self.rarity) is list:
            self.rarity_element_roll = True
            self.rarity = self.rarity[0]

        # Get guild information
        self.guild_mod = self.guild_table.get("tiers").get(self.rarity)
        self.guild_info = self.guild_table.get("gun_info")

        # Element rolling and parsing
        self.element = None
        self.element_info = []
        self.element_bonus = ""

        # Roll for element iff it has an appropriate guild and rarity
        if len(selected_elements) > 0:
            self.element = selected_elements
        elif self.guild_element_roll is True and self.rarity_element_roll is True:
            roll_element = str(randint(1, 100))
            roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

            element_table = get_file_data(base_dir + "resources/elements/elemental_table.json")
            self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # If the gun is Malefactor guild and it does not have an element yet, keep rolling until an element is picked
        if self.guild == "malefactor" and self.element is None:
            while self.element is None:
                roll_element = str(randint(1, 100))
                roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

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

        # Get element info if it exists
        if self.element is not None:
            for element in self.element:
                self.element_info.append(get_file_data(f"{base_dir}resources/elements/elemental_type.json").get(element))

        # Prefix parsing, either Random or Selected
        self.prefix_name = None
        self.prefix_info = None
        if prefix == "Random":
            roll_prefix = str(randint(1, 100))
        else:
            roll_prefix = prefix

        if prefix != "None":
            prefix_table = get_file_data(base_dir + "resources/guns/prefix.json").get(roll_prefix)
            self.prefix_name = prefix_table['name']
            self.prefix_info = prefix_table['info']
            self.name = self.prefix_name + ' ' + self.name

        # Red Text parsing, depending on the desired tier of randomness
        self.redtext_name = None
        self.redtext_info = None
        if redtext != "None":
            roll_redtext = redtext

        if redtext == "Random (All Rarities)":
            roll_redtext = str(randint(1, 100))

        if redtext == "Random (Epics+)" and self.rarity in ['epic', 'legendary']:
            roll_redtext = str(randint(1, 100))
        elif redtext == "Random (Epics+)":
            redtext = "None"

        if redtext == "Random (Legendaries)" and self.rarity == 'legendary':
            roll_redtext = str(randint(1, 100))
        elif redtext == "Random (Legendaries)":
            redtext = "None"

        if redtext != "None":
            redtext_table = get_file_data(base_dir + "resources/guns/redtext.json")
            redtext_item = redtext_table.get(self.get_redtext_tier(roll_redtext, redtext_table))
            self.redtext_name = redtext_item['name']
            self.redtext_info = redtext_item['info']

            # Check if Red Text adds an element and if that element is already applied
            if "Element type." in self.redtext_info:
                element = self.redtext_info.split(' ')[1].lower()

                # If there is no element, just simply add the element
                if self.element is None:
                    self.element = [element]
                    self.element_info = [get_file_data(base_dir + "resources/elements/elemental_type.json").get(element)]

                # Other check if element already is applied
                elif self.redtext_info.split(' ')[1].lower() not in self.element:
                    self.element.append(element)
                    self.element_info.append(get_file_data(base_dir + "resources/elements/elemental_type.json").get(element))

        # Check for combination elements
        self.element = self.convert_element(self.element)

        # Set file art path; sample if not given
        self.gun_art_path = ""
        if gun_art not in ["", None]:
            self.gun_art_path = gun_art
        else:
            self.gun_art_path = gun_images.sample_gun_image(self.type, self.guild)

    def get_random_ilevel(self, base_dir):
        """ Handles rolling for a random item level and giving back the tier key for it """
        roll_level = randint(1, 30)

        tier = None
        for key in get_file_data(base_dir + "resources/guns/gun_types.json").get("pistol").keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll_level <= upper:
                tier = key

        return tier

    def convert_element(self, elements):
        """ Handles converting a given element of various types into the parseable element icon path """
        if elements is None:
            return None

        # Check for combination elements and replace with combined element
        if "corrosive" in elements and "shock" in elements:
            elements.append("corroshock")
            elements.remove("corrosive")
            elements.remove("shock")

        if "explosive" in elements and "cryo" in elements:
            elements.append("explosivcryo")
            elements.remove("explosive")
            elements.remove("cryo")

        if "incendiary" in elements and "radiation" in elements:
            elements.append("incendiation")
            elements.remove("incendiary")
            elements.remove("radiation")

        return elements

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

    def get_redtext_tier(self, roll, redtext_table):
        """
        Handles getting the tier of redtext in which the given roll resides
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-100 random roll
        :param redtext_table: loaded in dictionary of redtext.json
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in redtext_table.keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll <= upper:
                tier = key

        return tier

    def __str__(self):
        """ Outputs a formatted block of the Guns' stats and what checks where made for elemental rolls """
        return  "Name: {}\n"\
                "Type: {}\n"\
                "Guild: {}\n" \
                "Rarity: {}\n" \
                "Item Level: {}\n"\
                "---\n"\
                "Damage: {}\n"\
                "Range: {}\n"\
                "Accuracy: {}\n"\
                "---\n"\
                "Guild Mod: {}\n"\
                "Guild Info:\n{}\n"\
                "---\n"\
                "Element Guild Check: {}\n"\
                "Element Rarity Check: {}\n"\
                "Element: {}\n"\
                "Element Info:\n{}\n"\
                "---\n"\
                "Prefix: {}\n"\
                "Prefix Info: {}\n"\
                "---\n"\
                "RedText: {}\n"\
                "RedText Info: {}\n".format(
            self.name, self.type, self.guild, self.rarity, self.item_level,
            self.damage, self.range, self.accuracy,
            self.guild_mod, self.guild_info,
            self.guild_element_roll, self.rarity_element_roll, self.element, self.element_info,
            self.prefix_name, self.prefix_info,
            self.redtext_name, self.redtext_info)
