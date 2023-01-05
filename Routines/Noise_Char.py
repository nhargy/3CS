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
t_exp = [1]

Noise_Run(t_exp, Run, s)
