import os
import re
import subprocess

sample_addr = "仙台市泉区泉中央二丁目1-1"
# sample_addr = "あいうえお"

# Path to the DAMS exec file built on the local env
dams_path = os.environ.get('DAMS')


def get_sh_result(addr):
    '''Run shell command (here DAMS search) for the address input'''

    cmd = subprocess.Popen(
        [dams_path, addr],
        stdout=subprocess.PIPE)
    scan_result = cmd.communicate()[0]
    return scan_result.decode()


def extract_info(dams_result_str=""):
    info = []
    for line in dams_result_str.splitlines():
        pass

    return info


extract_info(get_sh_result(sample_addr))
