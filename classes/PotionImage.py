"""
@file PotionImage.py
@author Ryan Missel

Handles filtering the scrapped game source dataset for specific properties for a given Potion image
"""
import json
import random
import requests

from PIL import Image


class PotionImage:
    def __init__(self, basedir):
        self.basedir = basedir

        # Rarity color mapping
        self.rarity_colors = {
            "common": [255, 255, 255, 0],
            "uncommon": [61, 210, 11, 255],
            "rare": [47, 120, 255, 255],
            "epic": [145, 50, 200, 255],
            "legendary": [255, 180, 0, 255]
        }

        # Concatenating all JSONs into one block
        with open(basedir + "resources/images/potion_images/bltps_ozkits.json", "r") as f:
            self.potion_data = json.load(f)

    def sample_potion_image(self):
        """ Handles sampling and downloading a relevant potion image from the games """
        url = random.sample(self.potion_data, 1)[0]['image_link']

        # Get image and then save locally temporarily
        response = requests.get(url, stream=True)
        img = Image.open(response.raw)
        img.save(self.basedir + 'output/potions/temporary_potion_image.png')
