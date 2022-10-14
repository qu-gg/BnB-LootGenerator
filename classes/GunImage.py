"""
@file GunImage.py
@author Chris Vantine

Handles filtering the scrapped game source dataset for specific properties, i.e. Hyperion manufacturer
"""
import json
import random
import requests
import cv2 as cv
import numpy as np

from PIL import Image


class GunImage:
    def __init__(self, prefix):
        self.prefix = prefix

        # List of individual JSONs
        PREFIX = prefix + "resources/images/gun_images/"
        FILELIST = [PREFIX + "bl1_guns.json", PREFIX + "bl2_guns.json",
                    PREFIX + "bl3_guns.json", PREFIX + "bltps_guns.json",
                    PREFIX + "blwl_guns.json"]

        # Manu and Type maps for conversion
        self.manu_map = {
            "alas!": "Atlas",
            "skuldugger": "Tediore",
            "feriore": "Tediore",
            "dahlia": "DAHL",
            "blackpowder": "Jakobs",
            "malefactor": "Maliwan",
            "hyperius": "Hyperion",
            "torgue": "Torgue"
        }

        self.type_map = {
            "combat_rifle": ['Assault Rifle'],
            "pistol": ['Pistol', 'Revolver', 'Repeater'],
            "shotgun": ['Shotgun'],
            "submachine_gun": ['SMG'],
            "sniper_rifle": ['Sniper'],
            "rocket_launcher": ['Launcher']
        }

        # Rarity color mapping
        self.rarity_colors = {
            "common": [255, 255, 255, 0],
            "uncommon": [61, 210, 11, 255],
            "rare": [47, 120, 255, 255],
            "epic": [145, 50, 200, 255],
            "legendary": [255, 180, 0, 255]
        }

        # Concatenating all JSONs into one block
        self.guns_data = []
        for filename in FILELIST:
            with open(filename, "r") as f:
                data = json.load(f)
                self.guns_data.extend(data)

        # Get statistics on types for conversions
        types = []
        manus = []
        for entry in self.guns_data:
            types.append(entry['type'])
            manus.append(entry['manufacturer'])

        self.types = np.unique(types)
        self.manus = np.unique(manus)

    def filter_guns_data(self, guns_data=None, gun_type=None, manufacturer=None, name=None):
        """
        Handles filtering the Guns data based on speciifc criterion, i.e. type, manu, name, etc.
        Recursive function that goes down the criterion on more and more filtered lists until reached
        :param guns_data: current iteration of the gun data
        :param gun_type: gun type to filter on
        :param manufacturer: manu to filter on
        :param name: name to search for
        :return: recursive call for more filtering or successfully filtered set
        """
        filtered_guns = []
        if name is not None:
            for item in guns_data:
                if item.get("name").lower() == name.lower():
                    filtered_guns.append(item)
                    print(item)
            return self.filter_guns_data(guns_data=filtered_guns, gun_type=gun_type, manufacturer=manufacturer)
        
        if manufacturer is not None:
            for item in guns_data:
                if item.get("manufacturer").lower() == manufacturer.lower():
                    filtered_guns.append(item)
            return self.filter_guns_data(guns_data=filtered_guns, gun_type=gun_type)
        
        if gun_type is not None:
            for item in guns_data:
                if item.get("type").lower() == gun_type.lower():
                    filtered_guns.append(item)
            return filtered_guns
        
        return guns_data

    def sample_gun_image(self, gun_type=None, manufacturer=None):
        """
        Handles sampling and downloading a relevant gun image from the games for gun card display use
        :param gun_type: type to filter on
        :param manufacturer: manu/guild
        """
        # Error catch if empty
        if gun_type is None and manufacturer is None:
            raise FileNotFoundError("No type or manufacturer given!")

        # Convert guild name
        manufacturer = self.manu_conversion(manufacturer)

        # Convert gun type
        gun_type = self.type_conversion(gun_type)

        # For each given gun type, get its filtered data and concatenate
        temp_data = []
        for entry in gun_type:
            temp_data.append(
                self.filter_guns_data(self.guns_data, entry, manufacturer)
            )

        gun_data = []
        for temp in temp_data:
            gun_data.extend(temp)

        # In the event of no images, just output the same image (even if it doesn't make sense)
        if len(gun_data) == 0:
            url = "https://global-uploads.webflow.com/5ff36780a1084987868ce198/618fd0cdd6736d4a1bbf5fbe_9-Volt%20(SMG-BL3).png"
        # Get a sample and its url link
        else:
            url = random.sample(gun_data, 1)[0]['image_link']

        # Get image and then save locally temporarily
        response = requests.get(url, stream=True)
        img = Image.open(response.raw)
        img.save(self.prefix + 'output/guns/temporary_gun_image.png')
        return url

    def manu_conversion(self, guild_name):
        """ Conversion table from game manu names to BnB guild names """
        return self.manu_map.get(guild_name)

    def type_conversion(self, gun_type):
        """ Conversion between BnB gun types to game gun types """
        return self.type_map.get(gun_type)
