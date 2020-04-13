# -*- coding: utf-8 -*-
import pandas as pd
import os
import time


def get_sheet_names(uri):
    '''Get the dict of every sheetname and its English translation'''

    xlsx = pd.ExcelFile(uri)

    # We're not interested in some redundant Excel sheets
    # Drop such sheets according to keywords from the sheet list
    key_sheet_names = [name for name in xlsx.sheet_names if
                       name.find("行政区別") == -1 and
                       name.find("合計") == -1]

    # Get the dict of sheetnames (JA as key, EN as value)
    return {sheet_name_ja: translate(sheet_name_ja)
            for sheet_name_ja in key_sheet_names}


def translate(ja_sheet_name):
    '''Tranlate lengthy Japanese name into English abbreviations'''
    '''e.g. convert "太白区（女）" into "taihaku_f" '''

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

    for ward_ja, ward_en in wards.items():
        if(ja_sheet_name.find(ward_ja) != -1):
            for gender_ja, gender_en in genders.items():
                if(ja_sheet_name.find(gender_ja) != -1):
                    return f'{ward_en}_{gender_en}'  # using f-strings


if __name__ == "__main__":
    start = time.time()
    xlsx_path = "./raw/age_each_r0204.xlsx"

    sheet_names = get_sheet_names(xlsx_path)
    print("Excel sheet names retrieved. Time elapsed:", time.time() - start)

    for sheet_name_ja, sheet_name_en in sheet_names.items():
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name_ja, header=1)

        # Remove the line break in a cell
        df.columns = df.columns.map(lambda x: x.replace('\n', ' '))

        df.to_csv(os.path.join(".", "csv", sheet_name_en + ".csv"),
                  mode="w",
                  index=True,
                  header=True)

        print("CSV output for", sheet_name_en,
              "Time elapsed:", time.time() - start)
