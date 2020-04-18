# -*- coding: utf-8 -*-
import pandas as pd
import constants
import position
import time
import matplotlib.pyplot as plt


def analyze_df(age_pos_df):
    '''Analyze the population indicators of the df given

    Args:
        age_pos_df (Pandas.DataFrame)
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

    town_codes = list(age_pos_df.town_code.unique())

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
        m_df = age_pos_df.loc[
            (age_pos_df.town_code == town_code) &
            (age_pos_df.gender == "m")]
        f_df = age_pos_df.loc[
            (age_pos_df.town_code == town_code) &
            (age_pos_df.gender == "f")]
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


def main(save_csv=False, save_json=False, save_hist=False):
    start = time.time()

    # Get the dataframe of age structures & positions
    #   of all the towns in Sendai
    df = position.merge_dfs()

    print("Calculating the statistics of the df...\n===")

    # Get statistical summary df from merged df
    df = analyze_df(df)

    if save_hist is True:
        plt.rcParams["font.family"] = constants.japanese_font

        ax = df.hist(column="pc_old", bins=50)

        for x in ax[0]:
            x.set_title("仙台市各町における老年人口比率の頻度分布", weight='bold')
            x.set_xlabel("老年人口比率（％）", weight='bold', size=10)
            x.set_ylabel("頻度", weight='bold', size=10)

        plt.savefig(constants.file_paths["AGEING_HIST_PNG"])

    if save_csv is True:
        print("Generating CSV file...\n===")
        df.to_csv(constants.file_paths["AGEGROUP_POS_CSV"],
                  mode="w",
                  index=True,
                  header=True)

    if save_json is True:
        print("Generating JSON file...\n===")

        # Drop unnecessary columns because JSON file size tends to be big
        df.drop(columns=["ward",
                         "town_code",
                         "dependency_ratio"],
                inplace=True)

        df.to_json(
            constants.file_paths["AGEGROUP_POS_JSON"],
            orient="split",
            force_ascii=False  # Output Japanese text as it is
        )

    print("Done.\nTime elapsed:", time.time() - start)


if __name__ == "__main__":
    main(
        save_hist=False,
        save_csv=True,
        save_json=False
    )
