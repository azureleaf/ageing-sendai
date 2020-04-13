# -*- coding: utf-8 -*-
import pandas as pd


def get_sheet_names(uri):
    '''Get the dict of every sheetname and its English translation'''

    xlsx = pd.ExcelFile(uri)

    # We're not interested in some Excel sheets
    # Drop the names of such sheets according to keywords
    key_sheet_names = [name for name in xlsx.sheet_names if
                       name.find("行政区別") == -1 and
                       name.find("合計") == -1]

    # Get the dict of sheetnames (JA as key, EN as value)
    return {sheet_name: translate(sheet_name)
            for sheet_name in key_sheet_names}


def translate(ja_sheet_name):
    '''Tranlate lengthy Japanese name into English abbreviations'''
    '''e.g. 太白区（女） into taihaku_f '''

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

    translation = ""
    for ward_ja, ward_en in wards.items():
        if(ja_sheet_name.find(ward_ja) != -1):
            translation += ward_en
            break
    for gender_ja, gender_en in genders.items():
        if(ja_sheet_name.find(gender_ja) != -1):
            translation += "_" + gender_en
            break
    return translation


if __name__ == "__main__":
    xlsx_path = "./raw/age_each_r0204.xlsx"

    # sheet_names = get_sheet_names(xlsx_path)
    # for sheet_name in sheet_names:
    #     pd.read_excel(xlsx_path,)
    print(translate("あああ太白区いaaaい男"))
