
#########################################
### 3CS Colour Centre Crystal Scanner ###
###          Python Library           ###
###     Author: Nadav Hargittai       ###
#########################################

"""
The following library hosts several functions related to the
operation of the 3CS experimental setup.
"""


# -- libraries --- #

# Devserve
from devserve.clients import SystemClient
# Instantiate
s = SystemClient.from_json_file("localhost", "D:3CS/CTRL/Server/dev_config.json")

# power meter libraries
import visa
from ThorlabsPM100 import ThorlabsPM100

# Horiba
import usb.core
import struct
import time

# OS
import os
import json
from datetime import datetime
import re
import numpy as np
import matplotlib.pyplot as plt

# -- -------- --- #

## REQUIRED VARIABLES FROM CONFIG FILE ##
# PATH_TO_SINGLE
path_to_single = 'D:\3CS\DATA\SingleExposures'
# PATH TO SCANS
path_to_scans = 'D:\3CS\DATA\_Scans_'
# PATH TO POWERCORRELATIONS
# PATH TO ELECTRONICNOISE


"""
Makes sure that the instantiation went smoothly and SystemClient
managed to load the device settings from the configuration file.
"""
def test():
    try:
        s.source_shutter.control = "computer"
        print("Listen out for the double clicking of the shutter!")
        s.source_shutter.on = True
        s.source_shutter.on = False
        print("Did you hear it? Then the setup was loaded properly.")
    except Exception:
        print("FAIL. Is the server running?")


"""
Zeros the system to predefined settings.
"""
def zero():
    
    source_power = 100;t_exp = 1;slit = 1000;spec_wl = 500;
    spec_gr = 1;mono_wl = 250;mono_gr = 0
    
    print("Zeroing... this may take a minute.")
    print()
    print(rf'Setting source power to {source_power}%...')
    s.source.power = source_power
    print('Setting computer shutter control...')
    s.source_shutter.control = "computer"
    print('Making sure the source and spectrometer shutter are closed...')
    s.source_shutter.on = False
    s.spectro.shutter = "closed"
    print('Making sure both flippers are down...')
    s.flipper.position = "down"
    s.flipperB.position = "down"
    s.spectro.shutter = "closed"
    print(rf"Setting exposure time to {t_exp} seconds...")
    s.spectro.exposure = t_exp
    print(rf"Setting spectrometer slit width to {slit} microns...")
    s.spectro.slit_width = slit
    print(rf"Setting spectrometer wavelength to {spec_wl}...")
    s.spectro.wavelength = spec_wl
    print(rf"Setting spectrometer grating to {spec_gr}...")
    s.spectro.grating = spec_gr
    print(rf"Setting monochromator wavelength to {mono_wl}...")
    s.horiba.wl = mono_wl
    print(rf"Setting monochromator grating to {mono_gr}...")
    s.horiba.gr = mono_gr
    print(rf"Setting power meter wavelengths to match the monochromator...")
    s.power_meter_a.wavelength = mono_wl
    s.power_meter_b.wavelength = mono_wl
    print("All done. System zeroed")
    print()


"""    
creates a unique ID string based on the current time
"""
def date_id():
    
    now = str(datetime.now())
    b = re.split('-| |:|',now)
    
    date = rf'{b[0]}-{b[2]}-{b[1]}-{b[3]}{b[4]}'
    
    return date


"""
excitation rules. take in a wavelength (of the monochromator) and returns the
required state of the system: filter wheels, gratings.
"""
def exc_rules(wl):
    spfw = 6
    lpfw = 6
    lpfw2 = 6
    grating = 1
    mono_grating = 0
    
    if wl < 250:
        spfw = 1
        lpfw = 6
        lpfw2 = 1
        grating = 1
        mono_grating = 0
        
    elif 250 <= wl < 267:
        spfw = 1
        lpfw = 6
        lpfw2 = 2
        grating = 1
        mono_grating = 0
        
    elif 267 <= wl < 275:
        spfw = 1
        lpfw = 6
        lpfw2 = 3
        grating = 1
        mono_grating = 0
        
    elif 275 <= wl < 320:
        spfw = 1
        lpfw = 6
        lpfw2 = 4
        grating = 1
        mono_grating = 0
    
    elif 320 <= wl < 380:
        spfw = 1
        lpfw = 1
        lpfw2 = 6
        grating = 1
        mono_grating = 0
        
    elif 380 <= wl < 440:
        spfw = 1
        lpfw = 2
        lpfw2 = 6
        grating = 2
        mono_grating = 1
    
    elif 440 <= wl < 490:
        spfw = 2
        lpfw = 3
        lpfw2 = 6
        grating = 2
        mono_grating = 1
        
    elif 490 <= wl < 540:
        spfw = 3
        lpfw = 4
        lpfw2 = 6
        grating = 2
        mono_grating = 1
        
    elif 540 <= wl < 590:
        spfw = 4
        lpfw = 5
        lpfw2 = 6
        grating = 2
        mono_grating = 1
        
    elif 590 <= wl:
        spfw = 5
        lpfw = 5
        lpfw2 = 6
        grating = 2
        mono_grating = 1
        
    return [grating,spfw,lpfw,lpfw2,mono_grating]


"""
return the x,y arrays from a file, given a starting line
"""
def read_xy(path,startline,split):
    
    # path     : str value specifying path to file
    # startline: int value specifying the line in the file from which to start reading
    # split    : str value specifying the string delineating the x value from the y values
    np.loadtxt(path, delimiter=split, skip=startline)
    sig = open(path,'r')
    x = []
    y = []
    Lines = sig.readlines()
    
    size = len(Lines)
    for line in range(startline,size):
        x_val = float(Lines[line].split(split)[0])
        y_val = float(Lines[line].split(split)[1])

        x.append(x_val)
        y.append(y_val)
    
    return x, y

"""
takes an exposure without regard to any settings
"""
def take_exposure():

    # take exposure
    s.source_shutter.on = True
    s.spectro.shutter= "open"
    s.spectro.running  = True
    s.spectro.shutter = "closed"
    powerval = s.power_meter_b.power
    time.sleep(0.1)
    s.source_shutter.on = False
    
    # generate unique date id
    now  = date_id()
    temp_id = rf'exp_{now}'
    
    # save file while making sure no overrides
    count = 1
    file_path = os.path.join(path_to_single,rf'{temp_id}.json')
    while os.path.exists(file_path) == True:
        file_path = os.path.join(path_to_single,rf'{temp_id}_({count}).json')
        count+=1
    
    s.spectro.save_path = file_path
    s.spectro.saved = True
    
    
    
    
    