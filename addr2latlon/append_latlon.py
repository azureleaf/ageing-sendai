import os
import re
import subprocess

sample_addr = "仙台市泉区泉中央二丁目1-12345"
# sample_addr = "あいうえお"

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


info = parse_dams_output(get_dams_output(sample_addr))
print(info)
