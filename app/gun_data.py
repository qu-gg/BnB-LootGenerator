import json


FILELIST = ["resources/bl1_guns.json", "resources/bl2_guns.json", "resources/bl3_guns.json", "resources/bltps_guns.json"]


class GunData:
    def __init__(self, filelist):
        self.guns_data = []
        for filename in filelist:
            with open(filename, "r") as f:
                data = json.load(f)
                self.guns_data.extend(data)


    def filter_guns_data(self, guns_data=None, gun_type=None, manufacturer=None, name=None):
        if guns_data is None:
            guns_data = self.guns_data

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

    def get_guns_data(self):
        return self.guns_data


if __name__ == "__main__":
    gd = GunData(FILELIST)
    data = gd.filter_guns_data(manufacturer='hyperion')
    print(data)