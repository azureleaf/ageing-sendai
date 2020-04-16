# -*- coding: utf-8 -*-
import pandas as pd
import constants
import time


def get_pos_df(pos_csv_path):
    # Load position csv, then extract necessary rows & columns
    df = pd.read_csv(pos_csv_path, encoding="shift_jis")
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
    # which are compatible with the df of age structure
    # e.g. "仙台市宮城野区" -> "miyagino"
    for ward_ja, ward_en in constants.wards.items():
        df = df.replace({"ward": rf'^.*{ward_ja}.*$'},
                        {"ward": ward_en}, regex=True)

    return df


def get_age_df(age_csv_path):
    # Load position csv, then drop unnecessary rows & columns
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


def analyze_df(full_df):
    '''Analyze the population indicators of the df given

    Args:
        full_df (Pandas.DataFrame)
    Returns:
        Pandas.DataFrame
    '''

    # Create the age classes list and group them into 3
    # We assume the format of input dataframe columns (e.g. "25-29")
    # Outcome will be like; {"young": ["0-4", "5-9", "10-14"...], ...}
    age_groups = {
        # 年少人口
        "young": [f'{i * 5}-{i * 5 + 4}' for i in range(0, 3)],
        # 生産年齢人口
        "working": [f'{i * 5}-{i * 5 + 4}' for i in range(3, 13)],
        # 老年人口
        "old": [f'{i * 5}-{i * 5 + 4}' for i in range(13, 18)]
    }
    age_groups["old"].append("90+")

    town_codes = list(full_df.town_code.unique())

    # Create dataframes for analysis result
    # Note: You can't calculate age average or age mean,
    # because age structure of people over 90+ isn't known
    summary_df = pd.DataFrame(columns=["ward",
                                       "town_code",
                                       "town_name",
                                       "total_pop",  # 総人口
                                       "pop_young",  # 年少人口
                                       "pop_working",  # 生産年齢人口
                                       "pop_old",  # 老年人口
                                       "pc_young",  # 年少人口比率 (%)
                                       "pc_working",  # 生産年齢人口比率 (%)
                                       "pc_old",  # 老年人口比率 (%)
                                       "gender_ratio",  # 男女比
                                       "ageing_index",  # 老年人口指数/老年化指数
                                       "dependency_ratio",  # 従属人口指数
                                       "lat",  # 緯度
                                       "lon",  # 経度
                                       ])

    for town_code in town_codes:
        row = {}
        row["town_code"] = town_code

        # Total population of this down by gender
        # Get partial dataframe for this town
        m_df = full_df.loc[
            (full_df.town_code == town_code) &
            (full_df.gender == "m")]
        f_df = full_df.loc[
            (full_df.town_code == town_code) &
            (full_df.gender == "f")]
        m_pop = m_df.total_pop.values[0]  # total men
        f_pop = f_df.total_pop.values[0]  # total women
        row["gender_ratio"] = \
            round(m_pop / f_pop * 100, 2) \
            if f_pop != 0 else None  # prevent zero division
        row["total_pop"] = m_pop + f_pop

        # Get values of this town
        # Both male & female rows have the identical values
        # for these columns, so pick m_df
        row["lat"] = m_df.lat.values[0]
        row["lon"] = m_df.lon.values[0]
        row["ward"] = m_df.ward.values[0]
        row["town_name"] = m_df.town_name.values[0]

        # Count the population & percentage data
        # for each of 3 age groups
        for group_name, age_classes in age_groups.items():
            # Dynamically set the name of the df columns
            # e.g. working_pop, working_pop_pc
            pop_col_name = "pop_" + group_name
            pc_col_name = "pc_" + group_name

            row[pop_col_name] = \
                m_df[age_groups[group_name]].values.sum() + \
                f_df[age_groups[group_name]].values.sum()
            row[pc_col_name] = \
                round(row[pop_col_name] / row["total_pop"] * 100, 2)

        # Calculate indicators
        row["ageing_index"] = \
            round(row["pop_old"] / row["pop_young"] * 100, 2) \
            if row["pop_young"] != 0 else None  # prevent zero division

        row["dependency_ratio"] = \
            round(
                (row["pop_old"] + row["pop_young"])
            / row["pop_working"] * 100, 2) \
            if row["pop_working"] != 0 else None  # prevent zero division

        # Append the data for this town to the df
        summary_df = summary_df.append(row, ignore_index=True)

    return summary_df


def analyze_and_save(output_format="csv"):
    '''Read age structure file, then save its stat summary to CSV'''
    start = time.time()

    # Convert CSVs into dataframes
    age_df = get_age_df(constants.file_paths["AGE_CSV"])
    pos_df = get_pos_df(constants.file_paths["POS_CSV"])

    # Inner-join 2 dataframes by town name & ward
    merged_inner = pd.merge(left=age_df,
                            right=pos_df,
                            on=["town_name", "ward"])

    print("Analyzing merged dataframes...\nTime elapsed:",
          time.time() - start, "\n===")

    # Get statistical summary df from merged df
    result_df = analyze_df(merged_inner)

    if output_format == "csv":
        print("Generating CSV file...")
        result_df.to_csv(constants.file_paths["AGEGROUP_POS_CSV"],
                         mode="w",
                         index=True,
                         header=True)

    if output_format == "json":
        print("Generating JSON file...")

        # Drop unnecessary columns because JSON file size tends to be big
        result_df.drop(columns=["ward",
                                "town_code",
                                "dependency_ratio"],
                       inplace=True)

        result_df.to_json(
            constants.file_paths["AGEGROUP_POS_JSON"],
            orient="split",
            force_ascii=False)

    print("Done.\nTime elapsed:", time.time() - start, "\n===")


# debug
if __name__ == "__main__":
    analyze_and_save(output_format="json")
