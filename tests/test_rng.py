"""
@file test_rng.py
@author Ryan Missel

Handles testing the distributions of gun stats over many trials to ensure
the generation is in-line with what is presented in the source rules
"""
import numpy as np
from tqdm import tqdm
from classes.Gun import Gun


if __name__ == '__main__':
    # Define lists to hold each trial generation
    types = []
    guilds = []
    item_level = []
    rarities = []
    elements = []
    malefactor = []

    # For X number of trials, generate a new gun and add its stats to each list
    for _ in tqdm(range(20000)):
        gun = Gun(None, None, None, None)

        types.append(gun.type)
        guilds.append(gun.guild)
        item_level.append(gun.item_level)
        rarities.append(gun.rarity)

        # Turning elements into strings
        if gun.element is None:
            elements.append("None")
        elif type(gun.element) == list:
            elements.append(''.join(gun.element))
        else:
            elements.append(gun.element)

        # Ensure that every Malefactor gun gets an element
        if gun.guild == "malefactor" and gun.element is not None:
            malefactor.append(1)
        elif gun.guild == "malefactor" and gun.element is None:
            malefactor.append(0)

    # Print out statistics to ensure
    print("Type Test:", np.unique(types, return_counts=True))
    print("Guild Test:", np.unique(guilds, return_counts=True))
    print("iLevel Test:", np.unique(item_level, return_counts=True))
    print("Rarity Test:", np.unique(rarities, return_counts=True))
    print("Element Test:", np.unique(elements, return_counts=True))
    print("Malefactor Test (expected 1s only):", np.unique(malefactor, return_counts=True))