# -*- coding: utf-8 -*-
import pandas as pd
import constants
import os.path
import age_structure


def get_pos_df(pos_csv_path):
    '''Load position csv as dataframe, format, and return'''

    df = pd.read_csv(pos_csv_path, encoding="shift_jis")

    # Extract necessary rows & columns
    df = df[["市区町村名", "大字町丁目コード", "大字町丁目名", "緯度", "経度"]]
    df = df.loc[df['市区町村名'].str.contains("仙台市")]

    # Translate the dataframe header
    replacements = {
        '市区町村名': 'ward',
        '大字町丁目コード': 'town_code',
        '大字町丁目名': 'town_name',
        '緯度': 'lat',
        '経度': 'lon',
    }
    for before, after in replacements.items():
        df.columns = df.columns.map(lambda x: x.replace(before, after))

    # Convert JA wards name into EN names
    #   which are compatible with the df of age structure
    # e.g. "仙台市宮城野区" -> "miyagino"
    for ward_ja, ward_en in constants.wards.items():
        df = df.replace({"ward": rf'^.*{ward_ja}.*$'},
                        {"ward": ward_en}, regex=True)

    return df


def get_age_df(age_csv_path):
    '''Load age structure CSV as dataframe, format and return'''

    df = pd.read_csv(age_csv_path, index_col=0)

    # Resolve discrepancies of town name notations
    # between position data & age data
    replacements = {
        "１丁目": "一丁目",
        "２丁目": "二丁目",
        "３丁目": "三丁目",
        "４丁目": "四丁目",
        "５丁目": "五丁目",
        "６丁目": "六丁目",
        "７丁目": "七丁目",
        "８丁目": "八丁目",
        "９丁目": "九丁目"
    }

    for before, after in replacements.items():
        df["town_name"] = df["town_name"] \
            .map(lambda name: name.replace(before, after))

    return df


def merge_dfs(output_csv=False):
    '''Read age structure file, then save its stat summary to CSV'''

    # When the dependency file doesn't exist, generate it
    if not os.path.isfile(constants.file_paths["AGE_CSV"]):
        age_structure.generate_csv()

    # Convert CSVs into dataframes
    age_df = get_age_df(constants.file_paths["AGE_CSV"])
    pos_df = get_pos_df(constants.file_paths["POS_CSV"])

    # Inner-join 2 dataframes by town name & ward
    merged_df = pd.merge(left=age_df,
                         right=pos_df,
                         on=["town_name", "ward"])

    if output_csv is True:
        # This file isn't dependency of any other scripts
        merged_df.to_csv(
            constants.file_paths["AGE_POS_CSV"],
            mode="w",
            index=True,
            header=True)

    print("Successfully merged two dataframes!\n===")
    return merged_df


# debug
if __name__ == "__main__":
    merge_dfs(output_csv=True)
