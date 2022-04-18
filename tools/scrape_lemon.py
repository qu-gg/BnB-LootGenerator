"""
@file scrape_lemon.py
@author Chris Vantine

Handles web scraping Lootlemon's database for all of its Borderlands gun art and stats over the 4 games.
"""
import bs4
import json
import requests

from tqdm import tqdm


# Define the Borderlands version to scrap from
BL_VERSION = "tps"


def main():
    # Get base weapon list for the given version
    url = "https://www.lootlemon.com/db/borderlands-{}/weapons".format(BL_VERSION)
    wep_url = "https://www.lootlemon.com/"
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # Define the array to hold all guns
    guns = []

    for link in tqdm(soup.find_all("div", "db_item")):
        # Get gun stats
        cells = link.find_all("div", "db_cell")
        new_gun = {}
        new_gun['name'] = cells[0].string
        new_gun['type'] = cells[1].string
        new_gun['manufacturer'] = cells[2].string

        # Get subURL for larger image
        try:
            weapon_url = link.find_all("a")[0]['href']
            sub_html = requests.get(wep_url + weapon_url).text
            sub_soup = bs4.BeautifulSoup(sub_html, 'html.parser')

            # Get image
            image_link = sub_soup.find_all("img", {"id": "page-image"})[0]['src']
            new_gun['image_link'] = image_link
        except:
            print("Error in Weapon {} for URL {}".format(cells[0].string, weapon_url))

        # Append to gun layout
        guns.append(new_gun)

    # Dump to JSON file
    with open(f"bl{BL_VERSION}_guns.json", "w") as f:
        f.writelines(json.dumps(guns))


if __name__ == "__main__":
    main()