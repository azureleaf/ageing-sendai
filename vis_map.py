import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import seaborn as sns
import os
import sys


def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information.
    """
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()  # get all the records
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)

    # assign(): Append a new column or update the existing column
    # Dataframe can be only 2-dimension, therefore
    # when a list is put into a cell, it will be converted to string
    # e.g. [1, 2, 3] => "[1, 2, 3]"
    df = df.assign(POINTS=shps)
    return df


def plot_shape_df(df):
    """ PLOTS A SINGLE SHAPE """

    fig, ax = plt.subplots()
    ax.margins(x=0.1, y=0.05)
    ax.set_aspect('equal')
    patches = []

    for index, row in df.iterrows():
        polygon = Polygon(row.POINTS, True)
        patches.append(polygon)

    p = PatchCollection(patches, alpha=0.8)
    colors = 100*np.random.rand(len(patches))
    p.set_array(np.array(colors))
    ax.add_collection(p)

    plt.xlim(140.4, 141)
    plt.ylim(38.1, 38.5)

    plt.show()

    return


def plot_shape_sf(sf, id, s=None):
    """ PLOTS A SINGLE SHAPE """
    # Plot figure
    plt.figure()

    # configure axis
    # aspect: vertical / horizontal ratio of the chart grid
    # set_aspect(num): "equal" means 1 : 1
    plt.axes().set_aspect('equal')

    # Extract the points of shape specified by id
    # format of points:
    #   [[x1, y1], [x2, y2], [x3, y3]...]
    # Order of points matters to draw polygon later:
    #   p1 -> p2 -> p3 -> p1 (closed polygon)
    shape_ex = sf.shape(id)

    # Generate the (x, 1) shape ndarray filled with 0
    #   format: np.zeros(tuple_which_tells_ndarray_shape)
    # x_lon: x(that is, lon) of points: [x1, x2, x3...]
    # y_lat: y(that is, lat) of points: [y1, y2, y3...]
    x_lon = np.zeros((len(shape_ex.points), 1))
    y_lat = np.zeros((len(shape_ex.points), 1))

    # Loop all the points of this shape
    for ip in range(len(shape_ex.points)):
        x_lon[ip] = shape_ex.points[ip][0]
        y_lat[ip] = shape_ex.points[ip][1]

    # Plot polygon based on
    plt.plot(x_lon, y_lat)

    # Centroid-ish point of the shape
    # These are mean, not midpoint
    x0 = np.mean(x_lon)
    y0 = np.mean(y_lat)
    plt.text(x0, y0, "Town", fontsize=10)

    # use bounding box to set plot limits
    # shape_ex.bbox has pos of 2 points:
    #   [x0, y0, xn, yn]
    plt.xlim(shape_ex.bbox[0], shape_ex.bbox[2])
    plt.ylim(shape_ex.bbox[1], shape_ex.bbox[3])

    plt.show()

    return x0, y0


def plot_map_sf(sf, x_lim=None, y_lim=None, figsize=(11, 9)):
    '''
    Plot map with lim coordinates
    '''
    plt.figure(figsize=figsize)
    id = 0
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x, y, 'k')

        if (x_lim is None) & (y_lim is None):
            x0 = np.mean(x)
            y0 = np.mean(y)
            plt.text(x0, y0, id, fontsize=10)
        id = id + 1

    if (x_lim is not None) & (y_lim is not None):
        plt.xlim(x_lim)
        plt.ylim(y_lim)


def visualize_map():
    regenerate_csv = False
    is_debug = False

    shape_csv_path = os.path.join(".", "csv", "sendai_shape.csv")
    shape_csv_sample_path = os.path.join(".", "csv", "sendai_shape_sample.csv")
    shp_path = os.path.join('.', 'raw', 'shapes', 'h27ka04.shp')

    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    sns.mpl.rc("figure", figsize=(10, 6))

    try:
        sf = shp.Reader(shp_path, encoding="shift_jis")
    except Exception as e:
        print("ERROR: Shape file doesn't exist:", type(e).__name__)
        sys.exit(1)

    # sf.shapes() returns the array of shape objects
    # print("Number of shapes in this file:", len(sf.shapes()))

    # Access to each shape
    # print("Sample the first file", sf.records()[0])

    df = read_shapefile(sf)
    df = df[df.GST_NAME == '仙台市']

    # Get the smallest index num (not always 0)
    # com_id = df.index.values[0]
    # print("com_id:", com_id)
    # plot_shape_sf(sf, com_id)
    # # plot_map_sf(sf)

    plot_shape_df(df)

    # save dataframe
    if is_debug is True:
        df.head(20).to_csv(shape_csv_sample_path,
                           mode="w",
                           index=True,
                           header=True)

    # save dataframe
    if regenerate_csv is True:
        df.to_csv(shape_csv_path,
                  mode="w",
                  index=True,
                  header=True)


if __name__ == "__main__":
    visualize_map()
