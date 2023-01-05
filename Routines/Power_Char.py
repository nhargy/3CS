# power meter libraries
import time
import visa
from ThorlabsPM100 import ThorlabsPM100

# Devserve
from devserve.clients import SystemClient 

# Measure Run
from States.MeasureRun import *

# Horiba
import usb.core
import struct
from datetime import datetime
import matplotlib.pyplot as plt


# Instantiate
try:
    s = SystemClient.from_json_file("localhost", "D:\\3CS\\CTRL\\Server\\dev_config.json")
except Exception as e:
    print(e)

### ---------------------------------------------------------------------###


Power_Run(s)
print()
input("Press Enter to Exit")



