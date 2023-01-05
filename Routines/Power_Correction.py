# Devserve
from devserve.clients import SystemClient

import visa
from ThorlabsPM100 import ThorlabsPM100

# Horiba
import usb.core
import struct
import time

# OS
import os
from datetime import datetime
import re
import numpy as np

# Instantiate
s = SystemClient.from_json_file("localhost", "D:/control_software/devserve - newdriver/examples/device_configuration.json")

from States.MeasureRun import *


### -----------------------------------------------------------------------###

print('Starting...')
time.sleep(0.5)

Run = 'ZnO_Run_202301041444'
Power_ID = 'PowCorr_202301041723'
Crystal = 'ZnO'

sig_path = rf"D:\\3CS\\DATA\\_Scans_\\{Run}\\BGR"

folder_path = rf'D:\\3CS\DATA\\_Scans_\\{Run}\\POWC'


if not os.path.exists(folder_path):
    os.mkdir(folder_path)


try:

    count = 0
    for filename in os.listdir(sig_path):
        save_path_name = os.path.join(folder_path,rf'{count}_{Crystal}_POWC.txt')
        f = os.path.join(sig_path,filename)
        Power_Correction(f,Power_ID,save_path_name)
        count+=1
except Exception as e:
    print(rf'Power corrected all {count} measurement files.')
    print()

time.sleep(0.5)

print('All done. Press Enter to exist')
input()
