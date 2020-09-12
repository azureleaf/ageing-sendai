'''
Read the CSV which has a column of addresses,
then append the columns of latitude & longitude for them
'''

import os
import re
import subprocess
import unittest
import pandas as pd
import numpy as np

# Path to the CSV path
facilities_csv_path = os.path.join("..", "raw", "facilities.csv")
output_csv_path = os.path.join("..", "results", "facilities_w_latlon.csv")

# Path to the DAMS exec file built on the local env
dams_path = os.environ.get('DAMS')


def get_dams_output(addr):
    '''Run shell command (here DAMS search) for the address input'''

    cmd = subprocess.Popen(
        [dams_path, addr],
        stdout=subprocess.PIPE)
    scan_result = cmd.communicate()[0]
    return scan_result.decode()


def parse_dams_output(dams_output=""):
    '''Parse the multi-line string into the accessible dict'''

    # Note: With Python, you can't use the variable as a dictionary key
    # Therefore create the tuple version first, then convert it into the dict
    info = []
    addr_parts = []

    for line in dams_output.splitlines():

        # Remove white spaces
        line = line.replace(" ", "")

        if re.match(r"(^tail=)|(^score=)", line):
            # Note that value may be empty for "tail="
            p = re.search(r"(.+)=(.*)", line)
            info.append(tuple([p.group(1), p.group(2)]))

        if re.match(r"^name=", line):
            params = line.split(",")
            addr_part_attrs = []

            for param in params:
                p = re.search(r"(.+)=(.+)", param)
                addr_part_attrs.append(tuple([p.group(1), p.group(2)]))

            addr_parts.append(dict(addr_part_attrs))

    info_dict = dict(info)
    info_dict["address_parts"] = addr_parts

    return info_dict


def csv2df(csv_path):
    '''Read the CSV supplied, return the Pandas dataframe for it'''

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("CSV file not found! Maybe the file name is incorrect.")
        return 1

    return df


def append_latlon(csv_path):
    '''
    Wrapper function to read the CSV,
    append coordinates, save it to another CSV'''

    df = csv2df(csv_path)
    addrs = df["address"]

    lat = pd.Series([], dtype="float64")
    lon = pd.Series([], dtype="float64")
    tail = pd.Series([], dtype="string")

    for i, addr in addrs.items():
        if addr is not np.nan:

            output = get_dams_output(addr)

            coord = parse_dams_output(output)["address_parts"]
            lat[i] = float(coord[-1]["y"])
            lon[i] = float(coord[-1]["x"])
            tail[i] = parse_dams_output(output)["tail"]

    df["lat"] = lat
    df["lon"] = lon
    df["tail"] = tail

    df.to_csv(output_csv_path, index=True)


class TestParsing(unittest.TestCase):
    def test_parsing(self):
        '''Run the local DAMS, parse the result output'''

        test_addr = "仙台市泉区泉中央二丁目1-12345"
        info = parse_dams_output(get_dams_output(test_addr))
        expected = str(7)
        actual = info["address_parts"][-1]["level"]
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    # unittest.main()

    append_latlon(facilities_csv_path)
