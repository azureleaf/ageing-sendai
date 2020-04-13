# -*- coding: utf-8 -*-
import pandas as pd
import os


def get_pos_df(pos_csv_path):
    # Load position csv, then drop unnecessary rows & columns
    df = pd.read_csv(pos_csv_path, encoding="shift_jis")
    df = df[["市区町村名", "大字町丁目名", "緯度", "経度"]]
    df = df.loc[df['市区町村名'].str.contains("仙台市")]

    replacements = {
        '市区町村名': 'ward',
        '大字町丁目名': 'town_name',
        '緯度': 'lat',
        '経度': 'lon',
    }
    for before, after in replacements.items():
        df.columns = df.columns.map(lambda x: x.replace(before, after))

    return df


def get_age_df(age_csv_path):
    # Load position csv, then drop unnecessary rows & columns
    df = pd.read_csv(age_csv_path)

    # Column names to be dropped from the dataframe
    ages = [str(age) for age in range(100)]
    print(len(ages))
    ages.append('100+')

    df = df.drop(columns=ages)

    # Resolve discrepancies of town names
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


if __name__ == "__main__":
    pos_csv_path = os.path.join(".", "raw", "04000-12.0b/04_2018.csv")
    age_csv_path = os.path.join(".", "csv", "age_structure.csv")

    pos_df = get_pos_df(pos_csv_path)
    print(pos_df)

    age_df = get_age_df(age_csv_path)
    print(age_df)
