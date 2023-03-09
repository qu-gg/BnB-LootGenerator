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

        # Tier to rarity mapping
        self.tier_to_rarity = {
            "1": "common",
            "2": "uncommon",
            "3": "rare",
            "4": "epic",
            "5": "legendary",
        }

        # Regex pattern for guild mod modifiers
        self.guild_mod_pattern = re.compile(r"\d\s[a-zA-Z]+\sMod", re.IGNORECASE)

    def export_gun(self, gun, output_name, redtext_check):
        """
        Handles exporting the generated gun in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/output/guns/
        :param gun: Gun object
        :param output_name: output filename assigned to the object
        :param redtext_check: whether to show or hide the redtext effect for the player
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/templates/fvtt_gun_template.json", 'r') as f:
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

        """ Cost """
        template["system"]["cost"] = gun.cost

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
        # Add gun damage base die to kinetic
        template["system"]["elements"]["kinetic"]["enabled"] = True
        template["system"]["elements"]["kinetic"]["damage"] = gun.damage

        # Elements enabling
        first_element = True
        if gun.element is not None:
            for key in template["system"]["bonusElements"].keys():
                if key in gun.element or (key == "crysplosive" and "explosivcryo" in gun.element):
                    template["system"]["bonusElements"][key]["enabled"] = True
                    template["system"]["bonusElements"][key]["damage"] = " "

                    # Just add elemental damage bonus to the first element for now
                    if first_element is True and gun.element_bonus != "":
                        template["system"]["bonusElements"][key]["damage"] = gun.element_bonus.replace("(+", "").replace(")", "")
                        first_element = False

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
            if self.guild_mod_pattern.match(modifier.replace("+", "").replace("-", "")):
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
        with open(f"{self.basedir}api/foundryVTT/output/guns/{output_name}.json", 'w') as f:
            json.dump(template, f)

    def export_shield(self, shield, output_name):
        """
        Handles exporting the generated shield in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/output/shields/
        :param shield: Shield object
        :param output_name: output filename assigned to the object
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/templates/fvtt_shield_template.json", 'r') as f:
            template = json.load(f)

        """ Foundry display information """
        template["name"] = shield.name
        template["img"] = shield.shield_art_path

        """ Item Level """
        template["system"]["level"] = int(shield.tier)

        """ Shield Effect + Description """
        template["system"]["effect"] = shield.effect
        template["system"]["description"] = shield.effect

        """ Rarity """
        template["system"]["rarity"]["name"] = self.tier_to_rarity[shield.tier].title()
        template["system"]["rarity"]["value"] = self.tier_to_rarity[shield.tier]
        template["system"]["rarity"]["colorValue"] = self.rarity_colors[self.tier_to_rarity[shield.tier]]

        """ Cost """
        template["system"]["cost"] = shield.cost

        """ Guild information """
        template["system"]["guild"] = shield.guild.title()

        """ Capacity and Recharge Rate """
        template["system"]["capacity"] = shield.capacity
        template["system"]["recoveryRate"] = shield.recharge

        """ Element information """
        if "Resistance" in shield.effect:
            effect = shield.effect.split(" ")
            resistance_die = effect[0]
            resistance_element = effect[1].lower()

            template["system"]["elements"][resistance_element]["enabled"] = True
            template["system"]["elements"][resistance_element]["damage"] = resistance_die

        # Saving shield json and image to folder
        with open(f"{self.basedir}api/foundryVTT/output/shields/{output_name}.json", 'w') as f:
            json.dump(template, f)

    def export_relic(self, relic, output_name):
        """
        Handles exporting the generated Relic in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/output/relics/
        :param relic: Relic object
        :param output_name: output filename assigned to the object
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/templates/fvtt_relic_template.json", 'r') as f:
            template = json.load(f)

        """ Foundry display information """
        template["name"] = relic.name
        template["img"] = relic.relic_art_path

        """ Relic Effect + Description """
        template["system"]["effect"] = relic.effect
        template["system"]["description"] = relic.effect

        """ Rarity """
        template["system"]["rarity"]["name"] = relic.rarity.title()
        template["system"]["rarity"]["value"] = relic.rarity
        template["system"]["rarity"]["colorValue"] = self.rarity_colors[relic.rarity]

        """ Cost """
        template["system"]["cost"] = relic.cost

        """ Class and Class Effect """
        template["system"]["class"] = relic.class_id
        template["system"]["classEffect"] = relic.class_effect

        # Saving relic json and image to folder
        with open(f"{self.basedir}api/foundryVTT/output/relics/{output_name}.json", 'w') as f:
            json.dump(template, f)

    def export_grenade(self, grenade, output_name):
        """
        Handles exporting the generated Grenade in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/output/grenades/
        :param grenade: grenade object
        :param output_name: output filename assigned to the object
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/templates/fvtt_grenade_template.json", 'r') as f:
            template = json.load(f)

        """ Foundry display information """
        template["name"] = grenade.name
        template["img"] = grenade.art_path

        """ Item Level """
        template["system"]["level"] = int(grenade.tier)

        """ Grenade Effect + Description """
        template["system"]["effect"] = grenade.effect
        template["system"]["description"] = grenade.effect

        """ Damage """
        template["system"]["damage"] = grenade.damage

        """ Rarity """
        template["system"]["rarity"]["name"] = self.tier_to_rarity[grenade.tier].title()
        template["system"]["rarity"]["value"] = self.tier_to_rarity[grenade.tier]
        template["system"]["rarity"]["colorValue"] = self.rarity_colors[self.tier_to_rarity[grenade.tier]]

        """ Cost """
        template["system"]["cost"] = grenade.cost

        """ Guild information """
        template["system"]["guild"] = grenade.guild.title()

        """ Elemental information """
        if grenade.element is not None:
            template["system"]["elements"][grenade.element]["enabled"] = True
            template["system"]["elements"][grenade.element]["damage"] = " "

        """ Detonation """
        if grenade.type == "Jumping":
            template["system"]["detonations"] = 2

        if grenade.type == "MIRV":
            template["system"]["detonations"] = 3

        """ Regain/Recharge Mechanics """
        if "gain health" in grenade.effect.lower():
            template["system"]["gainHealth"] = True

        if "recharges shields" in grenade.effect.lower():
            template["system"]["gainShield"] = True

        # Saving grenade json and image to folder
        with open(f"{self.basedir}api/foundryVTT/output/grenades/{output_name}.json", 'w') as f:
            json.dump(template, f)

    def export_potion(self, potion, output_name):
        """
        Handles exporting the generated potion in the FoundryVTT JSON format, saving both the JSON and gun art image
        in a folder output under api/foundryVTT/output/potions/
        :param potion: potion object
        :param output_name: output filename assigned to the object
        """
        # Loading in the template for gun items
        with open(f"{self.basedir}api/foundryVTT/templates/fvtt_potion_template.json", 'r') as f:
            template = json.load(f)

        """ Foundry display information """
        template["name"] = potion.name
        template["img"] = potion.art_path

        """ Potion Effect + Description """
        template["system"]["effect"] = potion.effect
        template["system"]["description"] = potion.effect

        """ Rarity """
        template["system"]["rarity"]["name"] = potion.rarity.title()
        template["system"]["rarity"]["value"] = potion.rarity
        template["system"]["rarity"]["colorValue"] = self.rarity_colors[potion.rarity]

        """ Cost """
        template["system"]["cost"] = potion.cost

        # Saving potion json and image to folder
        with open(f"{self.basedir}api/foundryVTT/output/potions/{output_name}.json", 'w') as f:
            json.dump(template, f)
