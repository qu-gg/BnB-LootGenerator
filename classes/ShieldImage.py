"""
@file ShieldImage.py
@author Ryan Missel

Handles filtering the scrapped game source dataset for specific properties for a given Shield image
"""
import json
import random
import requests

from PIL import Image


class ShieldImage:
    def __init__(self, basedir):
        self.basedir = basedir

        # List of individual JSONs
        PREFIX = basedir + "resources/images/shield_images/"
        FILELIST = [PREFIX + "bl2_shields.json", PREFIX + "bl3_shields.json",
                    PREFIX + "bltps_shields.json", PREFIX + "blwl_shields.json"]

        # Concatenating all JSONs into one block
        self.shields_data = []
        for filename in FILELIST:
            with open(filename, "r") as f:
                data = json.load(f)
                self.shields_data.extend(data)

    def sample_shield_image(self):
        """ Handles sampling and downloading a relevant Shield image from the games """
        url = random.sample(self.shields_data, 1)[0]['image_link']

        # Get image and then save locally temporarily
        response = requests.get(url, stream=True)
        img = Image.open(response.raw)
        img.save(self.basedir + 'output/shields/temporary_shield_image.png')
