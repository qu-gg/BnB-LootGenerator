"""
@file FoundryTranslator.py
@author Ryan Missel

Handles converting the Gun object state into a JSON formatted output to use in the B&B FoundryVTT system.
"""
import re
import json


class FoundryTranslator:
    def __init__(self, basedir, statusbar):
        super(FoundryTranslator, self).__init__()

        # Base directory of Python Executable
        self.basedir = basedir

        # PyQT statusbar to display messaages
        self.statusbar = statusbar

        # Color codes for rarity
        self.rarity_colors = {
            "common": "#a5a49f",
            "uncommon": "#0ea11f",
            "rare": "#00a0ff",
            "epic": "#7000a4",
            "legendary": "#ffa500"
        }

        # Regex pattern for guild mod modifiers
        self.pattern = re.compile(r"\d\s[a-zA-Z]+\sMod", re.IGNORECASE)

    def export_gun(self, gun, output_name, redtext_check):
        """
        Handles exporting the generated gun in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/outputs/guns/
        :param gun: Gun object
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/fvtt-gun-template.json", 'r') as f:
            template = json.load(f)

        """ Foundry display information """
        template["name"] = gun.name
        template["img"] = gun.gun_art_path

        """ Typing """
        template["system"]["type"]["name"] = gun.type.replace("_", " ").title()
        template["system"]["type"]["value"] = gun.type.replace("_", " ").lower()

        """ Item Level """
        template["system"]["level"] = int(gun.item_level.split("-")[0])

        """ Rarity """
        template["system"]["rarity"]["name"] = gun.rarity.title()
        template["system"]["rarity"]["value"] = gun.rarity.lower()
        template["system"]["rarity"]["colorValue"] = self.rarity_colors[gun.rarity.lower()]

        """ Guild information """
        template["system"]["guild"] = gun.guild.title()
        template["system"]["guildBonus"] = gun.guild_mod

        if gun.guild == "torgue":
            template["system"]["splash"] = True

        if gun.guild == "skuldugger":
            template["system"]["overheat"] = gun.guild_info.split("Overheat: ")[-1].replace('.', '')

        if gun.guild == "blackpowder":
            template["system"]["bonusCritDmg"] += int(gun.guild_mod.split(' ')[3])

        if gun.guild == "dahlia":
            template["system"]["hitBonus"] += 1

        """ RedText information """
        template["system"]["redText"] = gun.redtext_name if gun.redtext_name is not None else ""
        template["system"]["redTextEffect"] = gun.redtext_info if (redtext_check is False and gun.redtext_info is not None) else ""
        template["system"]["redTextEffectBM"] = gun.redtext_info if gun.redtext_info is not None else ""

        """ Element information """
        # Elements enabling
        first_element = True
        if gun.element is not None:
            for key in template["system"]["elements"].keys():
                if key in gun.element or (key == "crysplosive" and "explosivcryo" in gun.element):
                    template["system"]["elements"][key]["enabled"] = True
                    template["system"]["elements"][key]["damage"] = " "

                    # Just add elemental damage bonus to the first element for now
                    if first_element is True and gun.element_bonus != "":
                        template["system"]["elements"][key]["damage"] = gun.element_bonus.replace("(+", "").replace(")", "")
                        first_element = False

        # Add gun damage base die to kinetic
        template["system"]["elements"]["kinetic"]["enabled"] = True
        template["system"]["elements"]["kinetic"]["damage"] = gun.damage

        """ Prefix information"""
        template["system"]["prefix"]["name"] = gun.prefix_name if gun.prefix_name is not None else " "
        template["system"]["prefix"]["effects"] = gun.prefix_info if gun.prefix_name is not None else " "

        """ Damage information"""
        # Hit/Crit information
        template["system"]["accuracy"]["low"]["hits"] = gun.stats["accuracy"]["2-7"]["hits"]
        template["system"]["accuracy"]["low"]["crits"] = gun.stats["accuracy"]["2-7"]["crits"]

        template["system"]["accuracy"]["mid"]["hits"] = gun.stats["accuracy"]["8-15"]["hits"]
        template["system"]["accuracy"]["mid"]["crits"] = gun.stats["accuracy"]["8-15"]["crits"]

        template["system"]["accuracy"]["high"]["hits"] = gun.stats["accuracy"]["16+"]["hits"]
        template["system"]["accuracy"]["high"]["crits"] = gun.stats["accuracy"]["16+"]["crits"]

        # Range and damage
        template["system"]["damage"] = gun.damage
        template["system"]["range"] = int(gun.range)

        """ Stat mod modifiers """
        # Loop through each term in the guild mod, check against regex, and modify template values
        for modifier in gun.guild_mod.split(', '):
            if self.pattern.match(modifier.replace("+", "").replace("-", "")):
                modifier = modifier.split(' ')
                mod = int(modifier[0])
                stat = modifier[1].lower()
                template["system"]["statMods"][stat] += mod

        if gun.prefix_name == "Superb":
            template["system"]["statMods"]["acc"] += 1
            template["system"]["statMods"]["dmg"] += 1
            template["system"]["statMods"]["spd"] += 1
            template["system"]["statMods"]["mst"] += 1

        # Saving gun json and image to folder
        with open(f"{self.basedir}api/foundryVTT/outputs/guns/{output_name}.json", 'w') as f:
            json.dump(template, f)