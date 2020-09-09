import subprocess
import os

address = "仙台市泉区泉中央二丁目1-1"
dams_path = os.environ.get('DAMS')


cmd = subprocess.Popen(
    [dams_path, address],
    stdout=subprocess.PIPE)
scan_result = cmd.communicate()[0]
print(scan_result.decode())
