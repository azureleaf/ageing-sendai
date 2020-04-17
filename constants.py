# -*- coding: utf-8 -*-
import os

wards = {
    "青葉": "aoba",
    "太白": "taihaku",
    "泉": "izumi",
    "宮城野": "miyagino",
    "若林": "wakabayashi",
}

genders = {
    "男": "m",
    "女": "f"
}

file_paths = {
    # files downloaded
    "SHAPE_SHP": os.path.join('.', 'raw', 'shapes', 'h27ka04.shp'),
    "POS_CSV": os.path.join(".", "raw", "town-positions", "04_2018.csv"),
    "AGE_XLSX": os.path.join(".", "raw", "town-ages", "age_each_r0204.xlsx"),

    # files generated by python scripts
    "AGE_CSV": os.path.join(".", "results", "ages.csv"),
    "AGE_POS_CSV": os.path.join(".", "results", "ages_positions.csv"),
    "AGEGROUP_POS_CSV": os.path.join(
        ".", "results", "agegroups_positions.csv"),
    "AGEGROUP_POS_JSON": os.path.join(
        ".", "results", "agegroups_positions.json"),
    "SHAPE_CSV": os.path.join(".", "results", "shapes.csv"),
    "AGEING_HIST_PNG": os.path.join(".", "img", "ageing_hist.png"),
}

japanese_font = "Noto Sans CJK JP"
