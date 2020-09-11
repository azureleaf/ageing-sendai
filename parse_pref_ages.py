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


df_ages = csv2df(ages_path, skiprows=5, encoding="shift_jis")
df_shapes = csv2df(shapes_path)

print(df_ages["大字・町名"].head())
print(df_shapes["S_NAME"].head())
