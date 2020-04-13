# -*- coding: utf-8 -*-
import pandas as pd
import os
import time
# import sys


def get_sheet_names(uri):
    '''Get the dict of every sheetname and its English translation'''

    xlsx = pd.ExcelFile(uri)

    # We're not interested in some redundant Excel sheets
    # Drop such sheets according to keywords from the sheet list
    key_sheet_names = [name for name in xlsx.sheet_names if
                       name.find("行政区別") == -1 and
                       name.find("合計") == -1]

    # dict of sheetnames (JA name as key: EN name as value)
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


def format_df(df):
    '''Remove redundant rows / columns, and format data'''

    # Drop the columns of redundant data
    df.drop([column_name for column_name in df.columns if
             column_name.find("人口総数") != -1 or
             column_name.find("再掲") != -1
             ], axis=1, inplace=True)

    # Drop the last row of the redundant data (total population)
    df.drop([len(df.index) - 1], inplace=True)

    # Format the column indices for accessibility
    df.columns = df.columns.map(lambda x: x.replace('\n', ''))
    df.columns = df.columns.map(lambda x: x.replace('歳', ''))
    df.columns = df.columns.map(lambda x: x.replace('以上', '+'))
    df.columns = df.columns.map(lambda x: x.replace('町　名', 'town_name'))

    # Remove "字(aza)" rows,
    # because those numbers are already included in "大字(Oaza)"
    oaza_df = df[df['town_name'].str.contains("大字計")]
    aza_indices = []  # List of the indices of the rows to be dropped
    for i in oaza_df.index:
        oaza = df.loc[i]["town_name"].replace("（大字計）", "")
        df.loc[i]["town_name"] = oaza  # Modify original df as well

        # Trace the successive 字s which are included in the 大字
        # e.g. for oaza 茂庭, preceding rows are 茂庭字湯ノ沢, 茂庭字松倉... etc.
        while df.loc[i-1]["town_name"].find(oaza + "字") == 0:
            aza_indices.append(i-1)
            i -= 1
            if i <= 0:
                break

    # Drop the aza rows
    return df.drop(aza_indices)


if __name__ == "__main__":
    start = time.time()
    xlsx_path = "./raw/age_each_r0204.xlsx"

    # Seemingly reading Excel file takes quite a time
    sheet_names = get_sheet_names(xlsx_path)
    print("Excel sheet names retrieved. Time elapsed:", time.time() - start)

    for sheet_name_ja, sheet_name_en in sheet_names.items():
        print("Starting to process the sheet:", sheet_name_en)

        # Note: the "-" symbol is implicitly converted into value 0 here
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name_ja, header=1)

        df = format_df(df)

        df.to_csv(os.path.join(".", "csv", sheet_name_en + ".csv"),
                  mode="w",
                  index=True,
                  header=True)

        print("CSV output for", sheet_name_en,
              "Time elapsed:", time.time() - start)
