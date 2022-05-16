"""
@file RelicImage.py
@author Ryan Missel

Handles filtering the scrapped game source dataset for specific properties for a given relic image
"""
import json
import random
import requests

from PIL import Image


class RelicImage:
    def __init__(self, basedir):
        self.basedir = basedir

        # List of individual JSONs
        PREFIX = basedir + "resources/images/relic_images/"
        FILELIST = [PREFIX + "bl2_relics.json", PREFIX + "bl3_relics.json",
                    PREFIX + "bltps_relics.json", PREFIX + "blw_relics.json"]

        # Concatenating all JSONs into one block
        self.relics_data = []
        for filename in FILELIST:
            with open(filename, "r") as f:
                data = json.load(f)
                self.relics_data.extend(data)

    def sample_relic_image(self):
        """ Handles sampling and downloading a relevant relic image from the games """
        url = random.sample(self.relics_data, 1)[0]['image_link']

        # Get image and then save locally temporarily
        response = requests.get(url, stream=True)
        img = Image.open(response.raw)
        img.save(self.basedir + 'output/relics/temporary_relic_image.png')
