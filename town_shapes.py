import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import seaborn as sns
import sys
import constants


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
    # Dataframe can hold 2D matrix only, therefore
    #   a list put into a cell are implicitly stringified
    # e.g. [1, 2, 3] => "[1, 2, 3]"
    df = df.assign(POINTS=shps)
    return df


def get_bounding_box(polygons):
    '''
    Find the corners of the bounding box of the points given

    params:
        polygons (3D array):
            a inner-most array refers to a point (x, y)
    returns:
        (dict): Positions of 2 corner points
    '''

    flatten = np.asarray(
        [item for sublist in polygons for item in sublist])
    x_max, y_max = np.amax(flatten, axis=0)
    x_min, y_min = np.amin(flatten, axis=0)

    return {
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
    }


def plot_map_df(df, show_town_label=False):
    """
    Plots all the town shapes in the dataframe passed

    params:
        df (Pandas.DataFrame):
            Rows of towns and their detail info
        show_town_label (bool):
            True to add text label for every town
    """

    plt.rcParams["font.family"] = constants.japanese_font
    plt.rcParams["font.weight"] = "bold"

    fig, ax = plt.subplots()
    ax.margins(x=0.1, y=0.05)
    ax.set_aspect('equal')  # grid shape

    # Push town shapes to the list
    patches = []
    for index, row in df.iterrows():
        polygon = Polygon(row.POINTS, True)
        if show_town_label is True:
            plt.text(row.X_CODE, row.Y_CODE, row.S_NAME, fontsize=6)
        patches.append(polygon)

    # p = PatchCollection(patches, cmap=matplotlib.cm.Reds, alpha=0.6)
    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.6)
    colors = 100 * np.random.rand(len(patches))
    p.set_array(np.array(colors))
    ax.add_collection(p)

    # Set the size of the window
    corners = get_bounding_box(df.POINTS.values)
    plt.xlim(corners["x_min"], corners["x_max"])
    plt.ylim(corners["y_min"], corners["y_max"])

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


def trim_shape_df(df):
    '''Remove the unnecessary columnss from the dataframe'''

    # Extract the necessary columns
    df = df[[
        "KEY_CODE",  # 町名コード
        "S_NAME",  # 町名
        "CITY_NAME",  # 区名（政令指定都市以外では市名）
        "AREA",  # 面積
        "POINTS",  # 頂点座標群
        "X_CODE",  # 中心のx座標
        "Y_CODE",  # 中心のy座標
    ]]

    return df


def join_dfs(age_stat_df, shape_df):
    '''Merge 2 dataframes'''
    shape_df = shape_df.astype({'KEY_CODE': 'int64'})

    merged_df = pd.merge(left=age_stat_df,
                         right=shape_df,
                         left_on="town_code",
                         right_on="KEY_CODE")
    return merged_df


def visualize_map(
        output_shapes_csv=False,
        show_town_label=False,
):
    '''Read shapefile, convert it to df, then show in the viewer'''

    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    sns.mpl.rc("figure", figsize=(10, 6))

    try:
        sf = shp.Reader(
            constants.file_paths["SHAPE_SHP"],
            encoding="shift_jis")
    except Exception as e:
        print("ERROR: Shape file doesn't exist:", type(e).__name__)
        sys.exit(1)

    df = read_shapefile(sf)

    # Extract the Sendai city data only
    df = df[df.GST_NAME == '仙台市']

    if output_shapes_csv is True:
        # Save equivalent of the entire shapefile in CSV format
        df.to_csv(constants.file_paths["SHAPE_CSV"],
                  mode="w",
                  index=True,
                  header=True)

    # Extract the rows of towns in Sendai city
    df = trim_shape_df(df)

    plot_map_df(df, show_town_label)


if __name__ == "__main__":
    visualize_map(
        output_shapes_csv=False,
        show_town_label=True,
    )
