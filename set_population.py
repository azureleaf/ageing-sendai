# -*- coding: utf-8 -*-
import pandas as pd
import os
import time


def get_sheet_names(uri):
    '''Get the dict of every sheetname and its English translation'''

    xlsx = pd.ExcelFile(uri)

    # We're not interested in some Excel sheets with redundant data
    # Drop such sheets which have certain keywords
    key_sheet_names = [name for name in xlsx.sheet_names if
                       name.find("行政区別") == -1 and
                       name.find("合計") == -1]

    # dict of sheetnames (JA name as key: EN name as value)
    return {sheet_name_ja: translate(sheet_name_ja)
            for sheet_name_ja in key_sheet_names}


def translate(ja_sheet_name):
    '''Tranlate lengthy Japanese names into English abbreviations'''
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
    '''Remove redundant rows / columns, and format header'''

    # Drop the columns of redundant data
    df.drop([column_name for column_name in df.columns if
             column_name.find("人口総数") != -1
             ], axis=1, inplace=True)

    # Drop the last row of the redundant data (total population)
    df.drop([len(df.index) - 1], inplace=True)

    # Format the column names for better accessibility
    replacements = {
        '\n': '',
        '歳': '',
        '町　名': 'town_name',
        '（再掲）': '',
        '～': '-',
        '以上': '+'
    }
    for before, after in replacements.items():
        df.columns = df.columns.map(lambda x: x.replace(before, after))

    # Remove "字(aza)" rows,
    # because populations there are already counted in "大字(Oaza)"
    oaza_df = df[df['town_name'].str.contains("大字計")]
    aza_indices = []  # indices of the rows to be dropped
    for i in oaza_df.index:
        oaza = df.loc[i]["town_name"].replace("（大字計）", "")
        df.loc[i, "town_name"] = oaza  # Modify original df

        # Trace the successive 字s which are included in this 大字
        # e.g. for oaza 茂庭, preceding rows are 茂庭字湯ノ沢, 茂庭字松倉... etc.
        # Needs to abort the looping when it's the 1st row
        while i >= 1 and df.loc[i-1]["town_name"].find(oaza + "字") == 0:
            aza_indices.append(i-1)
            i -= 1

    # Drop those "aza" rows
    return df.drop(aza_indices)


def parse_xlsx(csv_dir=None):
    '''Parse Excel file of population-age distribution

    :param csv_dir: Relative path of the directory where CSV is to be output
        (optional. Specify only if you want the result as CSVs)
    :return: dictionary of dataframes
    '''
    start = time.time()
    xlsx_path = "./raw/age_each_r0204.xlsx"

    # Seemingly reading Excel file takes quite a time
    sheet_names = get_sheet_names(xlsx_path)
    print("Excel sheet names retrieved. Time elapsed:", time.time() - start)

    # Array of Pandas dataframes
    dfs = {}

    for sheet_name_ja, sheet_name_en in sheet_names.items():
        print("Processing the Excel sheet '", sheet_name_ja,
              "' Time elapsed:",  time.time() - start)

        # Note: the "-" symbol is implicitly converted into value 0 here
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name_ja, header=1)
        df = format_df(df)
        dfs[sheet_name_en] = df

    if (csv_dir is not None):
        # Sample header of a dataframe
        first_df_name = list(dfs.keys())[0]

        header = list(dfs[first_df_name].columns.values)
        header = ["ward", "gender"] + header

        merged_df = pd.DataFrame(columns=header)
        for df_name, df in dfs.items():
            ward, gender = df_name.split("_")  # e.g. taihaku_m
            df.insert(0, "gender", gender)  # e.g. m
            df.insert(0, "ward", ward)  # e.g. taihaku
            merged_df = pd.concat([merged_df, df], ignore_index=True)

        merged_df.to_csv(os.path.join(".", csv_dir, "age_structure.csv"),
                         mode="w",
                         index=True,
                         header=True)

    print("Completed! Total time elapsed:", time.time() - start)

    return dfs


# Debug purpose
if __name__ == "__main__":
    dfs = parse_xlsx("csv")
    # print(dfs)
