import bs4
import json
# import requests


HTML = """
Paste page HTML here. Reading from files is too jank.
"""


def main():
    # url = "https://www.lootlemon.com/db/borderlands-3/weapons"
    # html = requests.get(url).text
    soup = bs4.BeautifulSoup(HTML, 'html.parser')

    guns = []
    for item in soup.find_all("div", "db_item"):
        cells = item.find_all("div", "db_cell")
        image_links = item.find_all("img")
        image_link = ""
        for img in image_links:
            if 'png' in img['src']:
                image_link = img['src']

        new_gun = {}
        new_gun['name'] = cells[0].string
        new_gun['type'] = cells[1].string
        new_gun['manufacturer'] = cells[2].string
        new_gun['image_link'] = image_link

        guns.append(new_gun)
    
    bl_version = "2"
    with open(f"bl{bl_version}_guns.json", "w") as f:
        f.writelines(json.dumps(guns))


if __name__ == "__main__":
    main()