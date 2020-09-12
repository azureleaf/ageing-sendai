import pandas as pd
import os


ages_path = os.path.join("raw", "census_h27", "003_04.csv")
shapes_path = os.path.join("results", "shapes.csv")


def csv2df(csv_path, skiprows=0, encoding="utf-8"):
    try:
        df = pd.read_csv(csv_path, encoding=encoding, skiprows=skiprows)
    except FileNotFoundError:
        print("CSV file not found! Maybe the file name is incorrect.")
        return 1

    return df


def group_oaza_shapes(df_shapes):
    '''Create the group of polygons for every Oaza'''
    oazas = df_ages[df_ages["地域識別番号"] == 2]
    print(oazas["大字・町名"].head(20))


if __name__ == "__main__":
    df_ages = csv2df(ages_path, skiprows=5, encoding="shift_jis")
    df_shapes = csv2df(shapes_path)

    # Census data
    group_oaza_shapes(df_shapes)

    # Shape data
    # print(df_shapes["S_NAME"].head())
