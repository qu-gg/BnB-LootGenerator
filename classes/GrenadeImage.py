"""
@file GrenadeImage.py
@author Ryan Missel

Handles filtering the scrapped game source dataset for specific properties for a given Grenade image
"""
import json
import random
import requests

from PIL import Image


class GrenadeImage:
    def __init__(self, basedir):
        self.basedir = basedir

        # List of individual JSONs
        PREFIX = basedir + "resources/images/grenade_images/"
        FILELIST = [PREFIX + "bl2_grenades.json", PREFIX + "bl3_grenades.json", PREFIX + "bltps_grenades.json"]

        # Concatenating all JSONs into one block
        self.grenades_data = []
        for filename in FILELIST:
            with open(filename, "r") as f:
                data = json.load(f)
                self.grenades_data.extend(data)

    def sample_grenade_image(self):
        """ Handles sampling and downloading a relevant grenade image from the games """
        url = random.sample(self.grenades_data, 1)[0]['image_link']

        # Get image and then save locally temporarily
        response = requests.get(url, stream=True)
        img = Image.open(response.raw)
        img.save(self.basedir + 'output/grenades/temporary_grenade_image.png')
