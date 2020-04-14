import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(10, 6))

shp_path = os.path.join('.', 'raw', 'shapefile', 'h27ka04.shp')
sf = shp.Reader(shp_path, encoding="shift_jis")
print(len(sf.shapes()))

print(sf.records()[1])
