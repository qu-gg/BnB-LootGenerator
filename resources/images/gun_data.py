"""
@file gun_data.py
@author Chris Vantine

Handles filtering the scrapped game source dataset for specific properties, i.e. Hyperion manufacturer
"""
import json


class GunData:
    def __init__(self, filelist):
        # List of individual JSONs
        FILELIST = ["bl1_guns.json", "bl2_guns.json", "bl3_guns.json", "bltps_guns.json"]

        # Concatenating all JSONs into one block
        self.guns_data = []
        for filename in filelist:
            with open(filename, "r") as f:
                data = json.load(f)
                self.guns_data.extend(data)

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
