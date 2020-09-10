import os
import re
import subprocess
import unittest
import pandas as pd
import numpy as np

# Path to the CSV path
facilities_csv_path = os.path.join("..", "raw", "facilities.csv")

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
            p = re.search(r"(.+)=(.+)", line)
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
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("CSV file not found! Maybe the file name is incorrect.")
        return 1

    return df


def append_latlon(csv_path):

    df = csv2df(csv_path)
    addrs = df["address"]

    for i, addr in addrs.items():
        if addr is not np.nan:

            output = get_dams_output(addr)
            coord = parse_dams_output(output)["address_parts"]
            print(addr, coord)


class TestParsing(unittest.TestCase):
    def test_parsing(self):
        test_addr = "仙台市泉区泉中央二丁目1-12345"
        info = parse_dams_output(get_dams_output(test_addr))
        expected = str(7)
        actual = info["address_parts"][-1]["level"]
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    # unittest.main()

    # csv2df(csv_path)

    append_latlon(facilities_csv_path)
