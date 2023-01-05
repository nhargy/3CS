# Devserve
from devserve.clients import SystemClient 

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

Run = 'ZnO_Run_202301041545'
Crystal = 'ZnO'

sig_path = rf"D:\\3CS\\DATA\\_Scans_\\{Run}\\RAW"
noise_dict_path = rf'D:\\3CS\\DATA\\_Scans_\\{Run}\\BGR\\noise_dict.txt'
save_path = rf'D:\\3CS\\DATA\\_Scans_\\{Run}\\BGR'


count = 0
for filename in os.listdir(sig_path):
    save_path_name = os.path.join(save_path,rf'{count}_{Crystal}_BGR.txt')
    f = os.path.join(sig_path,filename)
    Noise_Cancellation(f,noise_dict_path,save_path_name)
    count+=1

print('All done. Press Enter to exist')
input()
