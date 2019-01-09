import ijson
from Doraemon.MySQL import mysql, settings
import re
import json
import csv
from itertools import islice


def imp_poi_openstreetmap(filepath):
    db = mysql.MySQL(settings.HOST, settings.USER_NAME, settings.PASS_WORD, settings.DATABASE)
    count_item = 0
    with open(filepath, 'r', encoding="utf-8") as f:
        objects = ijson.items(f, 'features.item')

        for item in objects:
            if "name" not in item["properties"]:
                continue
            name = item["properties"]["name"]

            names = set()
            names.add(name)

            other_tags_json_str = None
            if "other_tags" in item["properties"]:
                other_tags = item["properties"]["other_tags"]
                it = re.finditer('"(.*?)"=>"(.*?)"', other_tags)
                # tags_dict
                tags_dict = {}
                for match in it:
                    tags_dict[match.group(1)] = match.group(2)
                other_tags_json_str = json.dumps(tags_dict)

                # other names
                for key in tags_dict.keys():
                    if "name" in key:
                        names.add(tags_dict[key])

            coordinates = item["geometry"]["coordinates"]
            lon = float(coordinates[0])
            lat = float(coordinates[1])

            point_list = []
            for name in names:
                point = {
                    "name": name,
                    "longitude": lon,
                    "latitude": lat,
                    "other_tags": other_tags_json_str,
                }
                point_list.append(point)
            # print(json.dumps(point_list, indent=2))
            db.insert_many("poi_openstreetmap", point_list)
            count_item += 1
            print("----------------item: {}-------------".format(count_item))
    db.close_db()


def imp_poi_pku_open(filepath):
    db = mysql.MySQL(settings.HOST, settings.USER_NAME, settings.PASS_WORD, settings.DATABASE)

    try:
        seed_dict = json.load(open("./org_seed_dict_cn.json", "r"))
    except Exception:
        seed_dict = {}

    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        slice = islice(reader, 1, None)
        ind = 0
        while True:
            try:
                row = next(slice)
            except StopIteration:
                break
            except Exception:
                continue

            addr = row[0]
            adname = row[1]
            adcode = int(row[3])
            pname = row[4]
            cityname = row[5]
            name = row[6]
            location = row[7]
            type_ = row[9]
            if re.search("公司|企业|院校|学校|机构", type_):
                seed_dict[name] = 0

            loc_split = location.split("，")
            longitude = float(loc_split[0])
            latitude = float(loc_split[1])
            type_list = type_.split(";")

            poi = {
                "name": name,
                "longitude": longitude,
                "latitude": latitude,
                "pname": pname,
                "cityname": cityname,
                "adname": adname,
                "adcode": adcode,
                "address": addr,
                "type": json.dumps(type_list)
            }

            db.insert("poi_pku_open_research_data", poi)
            ind += 1
            if ind % 100000 == 0:
                print("pro: {}".format(ind))
        print("pro: {}".format(ind))
    db.close_db()

    json.dump(seed_dict, open("./org_seed_dict_cn.json", "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    # filename = "H:\\poi-data/asia.poi.json"
    # import_poi_openstreetmap(filename)

    import os
    import logging

    path_list = ["H:\\Projects/poi_pekinguni/2018-POICSV-1",
                 "H:\\Projects/poi_pekinguni/2018-POICSV-2",
                 "H:\\Projects/poi_pekinguni/2018-POICSV-3", ]
    for p in path_list:
        g = os.walk(p)
        for path, dir_list, file_list in g:
            for file_name in file_list:
                filepath = os.path.join(path, file_name)
                # filepath = "H:\\Projects/poi_pekinguni/2018-POICSV-1/1540880282990.csv"
                imp_poi_pku_open(filepath)
                logging.warning("{} done!".format(filepath))

    # filepath = "H:\\Projects/poi_pekinguni/2018-POICSV-1/1540880344601.csv"
    # imp_poi_pku_open(filepath)