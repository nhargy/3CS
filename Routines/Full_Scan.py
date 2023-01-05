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

### ----------------------------------------------------------------------- ###


crystal = input("Enter crystal name: ")
#workdir = input("Enter working directory: ")

min_wl = int(input("From wavelength: "))
max_wl = int(input("To wavelength: "))
step = int(input("Number of measurements: "))
exp = input("Spectrograph exposure time: ")
slit = input("Spectrograph slit width: ")
spec_wave = input("Spectrograph wavelength: ")

power_count = 10

print()
print("Finished taking inputs. ")

now = str(datetime.now())
b = re.split('-| |:|',now)
savedir = rf"{crystal}_Run_{b[0]}{b[1]}{b[2]}{b[3]}{b[4]}"
path_to_save = rf"D:\\3CS\\DATA\\_Scans_\\{savedir}"

if not os.path.exists(path_to_save):
    os.mkdir(path_to_save)

RAW_path = os.path.join(path_to_save,'RAW')

if not os.path.exists(RAW_path):
    os.mkdir(RAW_path)

initialise(exp,slit,s)
s.spectro.wavelength = spec_wave
s.power_meter_b.count = power_count
print("System initialised.")


state = [1,6,6,6,0] #[spec_grating,spfw,lpfw,lpfw2,mono_grating]
wl_range = np.linspace(min_wl,max_wl,step)
count = 0

print()
print("Starting measurements!")
print()


for wl in wl_range:
    
    print(str(count) +". Wavelength currently being set to: " + str(round(wl,1)) + "nm.")
    
    s.horiba.wl = round(wl,1)
    s.power_meter_b.wavelength = round(wl,1)

    new_state = exc_rules(wl)
    print(f"State updating to: Spectro grating={new_state[0]}, SPFW={new_state[1]}, LPFW={new_state[2]}, LPFW2={new_state[3]}, Mono grating={new_state[4]}")
    
    if new_state[0] == state[0]:
        pass
    else:
        s.spectro.grating = new_state[0]
        
    if new_state[1] == state[1]:
        pass
    else:
        s.spfw.position = new_state[1]
    
    if new_state[2] == state[2]:
        pass
    else:
        s.lpfw.position = new_state[2]
        
    if new_state[3] == state[3]:
        pass
    else:
        s.lpfw2.position = new_state[3]
        
    if new_state[4] == state[4]:
        pass
    else:
        s.horiba.gr = new_state[4]
    
    state = new_state
    
    print("State updated for "+str(round(wl,1)) +"nm.")
    print("Measuring...")
    
    #take measurement
    s.source_shutter.on = True
    s.spectro.shutter = "open"

    #s.power_meter_a.recording = True
    
    s.spectro.running  = True
    s.spectro.shutter = "closed"

    #s.power_meter_a.recording = False
    #powerval = s.power_meter_a.buffer_stats[2]
    powerval = s.power_meter_b.power

    s.source_shutter.on = False

    #power meter unit
    powerunit = s.power_meter_b.unit

    # save signal
    filename = os.path.join(RAW_path,rf"{count}_{crystal}.txt")
    s.spectro.save_path = filename
    s.spectro.saved = True

    # write more metadata
    data = ''
    data += 'link: '+ RAW_path +'\n'
    data += 'pm_read: '+str(powerval) +'\n'
    data += 'pm_unit: '+str(powerunit) +'\n'
    data += 'pm_count: '+str(power_count) +'\n'
    data += 'spfw: '+ str(state[1]) +'\n'
    data += 'lpfw: '+ str(state[2]) +'\n'
    data += 'lpfw2: '+ str(state[3]) +'\n'
    data += 'mono_grating: '+ str(state[4]) +'\n'
    data += 'mono_wavelength: '+ str(round(wl,1)) +'\n'
    data += 'spectro_grating: '+ str(state[0]) +'\n'
    data+='\n'

    with open(filename,'r') as fp:
        data2 = fp.read()
    data+=data2

    merged_path = os.path.join(RAW_path,rf'{count}-{crystal}.txt')
    merged = open(merged_path,'x')
    with open(merged_path,'w') as fp:
        fp.write(data)

    os.remove(filename)


    # IMPORTANT!!! PROGRAM GETS SLOW OTHERWISE
    s.spectro.clear_screen = True
    
    print(rf"Measurement completed and saved as {count}-{crystal}.txt . Moving on to next wavelength.")
    print()
    print()
    
    count+=1
        
print("All done. Press Enter to exit.")

input()
