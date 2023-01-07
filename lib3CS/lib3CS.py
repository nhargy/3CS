
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
from scipy import interpolate
import matplotlib.pyplot as plt

# -- -------- --- #

##   REQUIRED VARIABLES FROM CONFIG FILE   ##

# PATH_TO_SINGLE
path_to_single = 'D:\\3CS\\DATA\\SingleExposures'
# PATH TO SCANS
path_to_scans = 'D:\\3CS\\DATA\\_Scans_'
# PATH TO POWERCORRELATIONS
path_to_power = 'D:\\3CS\\DATA\\PowerCorrelations'
# PATH TO ELECTRONICNOISE
path_to_noise = 'D:\\3CS\\DATA\\ElectronicNoise'

##     LINE NUMBERS OF VALUES      ##
"""
The following is the standard layout of signal text file
"""

link_LINE =                         0
pm_read_LINE =                      1
pm_unit_LINE =                      2
pm_count_LINE =                     3
pm_wavelength_LINE =                4
spfw_LINE =                         5
lpfw_LINE =                         6
lpfw2_LINE =                        7
mono_grating_LINE =                 8
mono_wavelength_LINE =              9
spectro_grating_LINE =              10
# there's a space at line           11
Date_and_Time_LINE =                12
Software_Version_LINE =             13
Temperature_LINE =                  14
Model_LINE =                        15
Data_Type_LINE =                    16
Acquisition_Mode_LINE =             17
Trigger_Mode_LINE =                 18
Exposure_Time_LINE =                19
Readout_Mode_LINE =                 20
Horizontal_binning_LINE =           21
Extended_Dynamic_Range_LINE =       22
Horizontally_flipped_LINE =         23
Vertical_Shift_Speed_LINE =         24
Pixel_Readout_Rate_LINE =           25
Baseline_Clamp_LINE =               26
Clock_Amplitude_LINE =              27
Output_Amplifier_LINE =             28
Serial_Number_LINE =                29
Pre_Amplifier_Gain_LINE =           30
Spurious_Noise_Filter_Mode_LINE =   31
Photon_counted_LINE =               32
Data_Averaging_Filter_Mode_LINE =   33
SR193i_LINE =                       34
Serial_Number_LINE =                35
Wavelength_LINE =                   36
Grating_Groove_Density_LINE =       37
Grating_Blaze_LINE =                38
Input_Side_Slit_Width_LINE =        39
# there's a space at line           40
# there's a space at line           41
# there's a space at line           42
start =                             43


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
    
    source_power = 100; t_exp = 1; slit = 1000; spec_wl = 500; spfw = 6
    lpfw=6; lpfw2=6; spec_gr = 1; mono_wl = 250; mono_gr = 0
    
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
    print(rf'Setting all the filters to {spfw}...')
    s.spfw.position = spfw
    s.lpfw.position = lpfw
    s.lpfw2.position = lpfw2
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
Lets the user manually change system settings.
"""
def ctrl(source_power = None, source_shutter_control = None, source_shutter = None, spfw = None, lpfw = None, lpfw2 = None, flipper = None, flipperB = None, mono_wl = None, mono_gr = None, spec_gr = None, spec_wl = None, spec_exp = None, spec_slit = None, spec_shutter = None, spec_running = None, spec_save_path = None, spec_saved = None, power_meter_a_count = None, power_meter_b_count = None, power_meter_a_power = None, power_meter_b_power = None, power_meter_a_unit = None, power_meter_b_unit = None):
    
    if source_power != None:
        print(rf'Setting source_power to {source_power}%')
        s.source.power = source_power
        
    if source_shutter_control != None:
        print(rf'Setting source shutter to {source_shutter_control} control')
        s.source_shutter.control = source_shutter_control

    if source_shutter != None:
        print(rf'Source shutter on is {source_shutter}')
        s.source_shutter = source_shutter

    if spfw != None:
        print(rf'Setting spfw to position {spfw}')
        s.spfw.position = spfw
        
    if lpfw != None:
        print(rf'Setting lpfw to position {lpfw}')
        s.lpfw.position = lpfw
        
    if lpfw2 != None:
        print(rf'Setting lpfw2 to position {lpfw2}')
        s.lpfw2.position = lpfw2
        
    if flipper != None:
        print(rf'Flipper set to {flipper}')
        s.flipper.position = flipper
        
    if flipperB != None:
        print(rf'FlipperB set to {flipperB}')
        s.flipperB.position = flipperB
        
    if mono_wl != None:
        print(rf'Setting monochromator wavelength to {mono_wl}nm')
        s.horiba.wl = mono_wl
        
    if mono_gr != None:
        print(rf'Setting monochromator grating to {mono_gr}')
        s.horiba.gr = mono_gr
        
    if spec_gr != None:
        print(rf'Setting spectrometer grating to {spec_gr}')
        s.spectro.grating = spec_gr
        
    if spec_wl != None:
        print(rf'Setting spectrometer wavelength to {spec_wl}')
        s.spectro.wavelength = spec_wl
        
    if spec_exp != None:
        print(rf'Setting spectrometer exposure time to {spec_exp}')
        s.spectro.exposure = spec_exp
        
    if spec_slit != None:
        print(rf'Setting spectrometer slit width to {spec_slit} microns')
        s.spectro.slit_width = spec_slit
        
    if spec_shutter != None:
        print(rf'Spectrometer shutter is {spec_shutter}')
        s.spectro.shutter = spec_shutter
        
    if spec_running != None:
        print()
        print('Taking data...')
        print()
        s.spectro.running = spec_running
        
    if spec_save_path != None:
        s.spectro.save_path = spec_save_path
        
    if spec_saved != None:
        s.spectro.saved = spec_saved
        print('Spectrometer data saved.')
        print()
        
    if power_meter_a_count != None:
        print(rf'Power meter a count set to {power_meter_a_count}')
        s.power_meter_a.count = power_meter_a_count
        
    if power_meter_b_count != None:
        print(rf'Power meter b count set to {power_meter_b_count}')
        s.power_meter_b.count = power_meter_b_count
        
    if power_meter_a_power == True:
        pow_a = s.power_meter_a.power
        print('Power meter a: '+str(pow_a))
        
    if power_meter_b_power == True:
        pow_b = s.power_meter_b.power
        print('Power meter b: '+str(pow_b))
        
    if power_meter_a_unit == True:
        pow_a_unit = s.power_meter_a.unit
        print('Unit of power meter a: '+str(pow_a_unit))
        
    if power_meter_b_unit == True:
        pow_b_unit = s.power_meter_b.unit
        print('Unit of power meter b: '+str(pow_b_unit))
        
    print()
    print('All set.')
    return None



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
def read_xy(path,startline,split=None,col=2):
    
    # path     : str value specifying path to file
    # startline: int value specifying the line in the file from which to start reading
    # split    : str value specifying the string delineating the x value from the y values
    if col == 2:
        x, y = np.loadtxt(path, delimiter=split, skiprows=startline).T
        x = x.astype(np.float);y = y.astype(np.float)
        return x, y
        
    elif col == 3:
        w, x, y = np.loadtxt(path, delimiter=split, skiprows=startline).T
        w = w.astype(np.float);x = x.astype(np.float);y = y.astype(np.float)
        return w, x, y
    
    

"""
takes a string as input (e.g. 'power') and return that measurement's value of the requested value
""" 
def read_value(path,value,split=None):
    
    file = open(path,'r')
    Lines = file.readlines()
    
    if value == 'power':
        req_val = float(Lines[pm_read_LINE].split()[1])
        
    elif value == 'power unit':
        req_val = Lines[pm_unit_LINE].split()[1]
        
    elif value == 'power count':
        req_val = float(Lines[pm_count_LINE].split()[1])
        
    elif value == 'power wl':
        req_val = float(Lines[pm_wavelength_LINE].split()[1])
        
    elif value == 'spfw':
        req_val = int(Lines[spfw_LINE].split()[1])
        
    elif value == 'lpfw':
        req_val = int(Lines[lpfw_LINE].split()[1])
        
    elif value == 'lpfw2':
        req_val = int(Lines[lpfw2_LINE].split()[1])
        
    elif value == 'mono gr':
        req_val = int(Lines[mono_grating_LINE].split()[1])
        
    elif value == 'mono wl':
        req_val = float(Lines[mono_wavelength_LINE].split()[1])
        
    elif value == 'spec gr':
        req_val = int(Lines[spectro_grating_LINE].split()[1])
        
    elif value == 'temp':
        req_val = float(Lines[Temperature_LINE].split()[2])
        
    elif value == 't':
        req_val = float(Lines[Exposure_Time_LINE].split()[3])
    
    return req_val



"""
simply plots the signal in a convenient form
"""
def plot_signal(path,save_path,startline,split=None,colour='darkred',xl = r'Wavelength $[nm]$',yl = 'Photon Count',title = rf'Exposure Signal',save=False):
    
    plt.rcParams["figure.figsize"] = 12, 4
    
    x,y = read_xy(path,startline,split)
    
    plt.plot(x,y,color=colour)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.grid('on')
    plt.title(title)
    
    if save == False:
        plt.show()
        
    elif save ==  True:
        plt.savefig(save_path)
    
    return None
    


"""
saves a value to a file as a string 
"""   
def save_string(string,path,newline):
    with open(path, 'a') as f:
        if newline == True:
            f.write(string)
            f.write('\n')
        else:
            f.write(string)
            
    return None



"""
writes the top part of the standard file format containing the metadata to a string
"""   
def gather_metadata(baseline=False):

    print('Gathering metadata... this may take a minute.')
    
    data = ''
    data += 'link: '+ path_to_single +'\n'
    
    if baseline == False:
        powerval = s.power_meter_b.power 
        data += 'pm_read: '+str(powerval) +'\n'
        
        powerunit = s.power_meter_b.unit
        data += 'pm_unit: '+str(powerunit) +'\n'
        
        power_count = s.power_meter_b.count
        data += 'pm_count: '+str(power_count) +'\n'
        
        power_wavelength = s.power_meter_b.wavelength
        data += 'pm_wavelength: '+str(power_wavelength) +'\n'
        
    elif baseline == True:
        data += 'pm_read: '+ 'NA' +'\n'
    
        data += 'pm_unit: '+'NA' +'\n'
        
        data += 'pm_count: '+'NA' +'\n'
        
        data += 'pm_wavelength: '+'NA' +'\n'
             
    
    data += 'spfw: '+ str(s.spfw.position) +'\n'
    data += 'lpfw: '+ str(s.lpfw.position) +'\n'
    data += 'lpfw2: '+ str(s.lpfw2.position) +'\n'
    data += 'mono_grating: '+ str(s.horiba.gr) +'\n'
    data += 'mono_wavelength: '+ str(round(s.horiba.wl,1)) +'\n'
    data += 'spectro_grating: '+ str(s.spectro.grating) +'\n'
    data+='\n'
    
    return data


"""
takes in a string of metadata and file path to spectrometer measurement text file and creates a new
standard file format, while deleting the raw spectrometer file
"""   
def make_standard(spec_file, data,save_path):
    
    # merge metadata with signal data
    with open(spec_file,'r') as fp:
        data2 = fp.read()
        data+=data2
    
    open(save_path,'x')
    with open(save_path,'w') as fp:
        fp.write(data)
        
    os.remove(spec_file)
    print(rf'Saved signal to: {save_path} .')
    
    return None


"""
takes an exposure without regard to any settings, for simple user interface.
if baseline set to True, then the shutters remain closed
"""
def take_exposure(baseline=False):

    if baseline == False:

        # take exposure
        s.source_shutter.on = True
        s.spectro.shutter= "open"
        print('Taking exposure...')
        s.spectro.running  = True
        print('Done')
        s.spectro.shutter = "closed"
        powerval = s.power_meter_b.power
        time.sleep(0.1)
        s.source_shutter.on = False
        
    elif baseline == True:
        s.source_shutter.on = False
        s.spectro.shutter = 'closed'
        print('Taking exposure...')
        s.spectro.running  = True
        print('Done')
        powerval = s.power_meter_b.power
        time.sleep(0.1)
    
    print('Generating plot...')
    # generate unique date id
    now  = date_id()
    temp_id = rf'exp_{now}'
    
    # save file while making sure of no overrides
    count = 1
    file_path = os.path.join(path_to_single,rf'{temp_id}_(0).txt')
    while os.path.exists(file_path) == True:
        file_path = os.path.join(path_to_single,rf'{temp_id}_({count}).txt')
        count+=1

    s.spectro.save_path = file_path
    s.spectro.saved = True
    
    plot_signal(file_path,'',31)
    
    time.sleep(1)
    
    query = input('Save this signal? (y or n): ')
    if (query == 'y') or (query == 'Y'):
        crystal = input('Enter the name of the crystal/exposure type: ')
        perm_id = rf'{crystal}_{now}'
        
        folder_path = os.path.join(path_to_single,rf'{perm_id}')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        query2 = input('Add a comment here (or leave empty): ')
        if query2 != None:
            comment_path = os.path.join(folder_path,'comments.txt')
            if not os.path.exists(comment_path):
                open(comment_path,'x')
            with open(comment_path,'w') as fp:
                fp.write(query2)

        save_path =  os.path.join(folder_path,rf'{perm_id}.txt')
        data = gather_metadata()
        make_standard(file_path,data,save_path)

        fig_path = os.path.join(folder_path,rf'{crystal}_plot.png')
        plot_signal(save_path,fig_path,start,title=rf'{perm_id}',save=True)
        plt.close()
        
    else:
        os.remove(file_path)
        print()
        print('Did not save signal.')
        
    return None



"""
takes power correlation data between power meters A and B
"""
def take_power(min_wl, max_wl,step):
    
    # zero the system before starting
    zero()
    
    now = date_id()
    pow_id = rf'PowCorr_{now}'
    
    folder_path = os.path.join(path_to_power,pow_id)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    wl_vals = np.arange(min_wl,max_wl,step)
    gratings = [0,1]
    
    # loop through the two gratings
    for i in gratings:

        print(rf"Starting measurements for grating {i}!")
        print()

        # open source shutter:
        s.source_shutter.control = "computer"
        s.source_shutter.on = True

        # set grating
        s.horiba.gr = i

        # make sure pm set to power
        s.power_meter_a.unit = 0
        s.power_meter_b.unit = 0

        # create file
        path = os.path.join(folder_path, rf'pow_gr{i}.txt')
        open(path, "x")

        # save metadata
        save_string(rf'Date: {now}',path,True)
        save_string('Mono_grating: '+str(s.horiba.gr),path,True)
        save_string('',path,True)

        count = 0
        for wl in wl_vals:
            print(rf'{count}. Setting wavelength to: '+str(wl))
            s.horiba.wl = wl
            s.power_meter_a.wavelength = wl
            s.power_meter_b.wavelength = wl

            #get power reading
            print('Getting power...')
            power_read_a = s.power_meter_a.power
            power_read_b = s.power_meter_b.power

            #save measurement
            save_string(str(wl)+' ',path,False)
            save_string(str(power_read_a)+' ',path,False)
            save_string(str(power_read_b),path,True)

            count+=1
            print('Measurement recorded successfully.')
            print()
            print()
            
    s.source_shutter.on = False
    print('All done.')
    
    return None
    
    
    
"""
analyses the power ratio between B and A, and returns two interpolated functions for the ratio as a function
of wavelength, one for each monochromator grating.
"""
def analyse_power(pow_id):
    
    file0_path = rf'D:/3CS/DATA/PowerCorrelations/{pow_id}/pow_gr{0}.txt'
    file1_path = rf'D:/3CS/DATA/PowerCorrelations/{pow_id}/pow_gr{1}.txt'
    
    wl0,a0,b0 = read_xy(file0_path,3,split=' ',col=3)
    wl1,a1,b1 = read_xy(file1_path,3,split=' ',col=3)
    
    b0_over_a0 = np.divide(b0,a0)
    b1_over_a1 = np.divide(b1,a1)
    
    ratio_path = rf'D:/3CS/DATA/PowerCorrelations/{pow_id}/pow_ratio.txt'
    if not os.path.exists(ratio_path):
        np.savetxt(ratio_path,np.array([wl0,b0_over_a0,b1_over_a1]).T,delimiter=' ')
    
    ratio0 = interpolate.interp1d(wl0, b0_over_a0)
    ratio1 = interpolate.interp1d(wl1, b1_over_a1)
    
    inter_b0_over_a0 = ratio0(wl0)
    inter_b1_over_a1 = ratio1(wl1)
    
    plt.rcParams["figure.figsize"] = 15, 4
    
    figure, axis = plt.subplots(1, 2)
    
    axis[0].scatter(wl0,b0_over_a0, s=7,color='darkred')
    axis[0].plot(wl0,inter_b0_over_a0, '-',color='red',label='Mono_grating 0')
    axis[0].scatter(wl1,b1_over_a1, s=7,color='darkblue')
    axis[0].plot(wl1,inter_b1_over_a1, '-',color='blue',label='Mono_grating 1')
    
    axis[0].grid('on')
    axis[0].legend()
    axis[0].set_title('Power meter ratio: '+ pow_id)
    axis[0].set_xlabel(r'Excitation wavelength $[nm]$')
    axis[0].set_ylabel('B/A')
    
    axis[1].plot(wl0,np.multiply(a0,1e6),color='darkgreen',label='Mono_grating 0')
    axis[1].plot(wl0,np.multiply(b0,1e6),'--',color='darkgreen')
    axis[1].plot(wl1,np.multiply(a1,1e6),color='purple',label='Mono_grating 1')
    axis[1].plot(wl1,np.multiply(b1,1e6),'--',color='purple')
    
    axis[1].grid('on')
    axis[1].legend()
    axis[1].set_title('Monochromator efficiency: '+pow_id)
    axis[1].set_xlabel(r'Excitation wavelength $[nm]$')
    axis[1].set_ylabel(r'Power [$\mu W$]')
    
    img_path = rf'D:/3CS/DATA/PowerCorrelations/{pow_id}/pow_ratio_plot.png'
    if not os.path.exists(img_path):
        plt.savefig(img_path)
    
    plt.show()
    
    return ratio0, ratio1



"""
takes two inputs: the path of signal to be corrected and the power id of the specific calibration to be used,
and returns the corrected array (wl vs photon_per_photon) together with its metadata from the signal path
"""
def correct_power(sig_path,pow_id):
    
    # get the interpolated power ratios
    fun0, fun1 = analyse_power(pow_id)
    
    # get the sample power reading of the signal
    sample_power = read_value(sig_path,'power')
    
    # get the monochromator grating value
    mono_gr = read_value(sig_path,'mono gr')
    
    # get the exposure time of the signal
    t = read_value(sig_path, 't')
    
    # get the wavelength of the reading
    mono_wl = read_value(sig_path,'mono wl')
    power_wl = read_value(sig_path,'power wl')
    if mono_wl != power_wl:
        raise Exception(rf"Monochromator and power meter b do not agree on their wavelengths: {mono_wl} vs {pow_wl}")
    
    # calculate total photon count from sample
    h = 6.626070151e-34
    c = 299792458
    if mono_gr == 0:
        ratio = fun0(mono_wl)
    elif mono_gr == 1:
        ratio = fun1(mono_wl)
        
    total_power = sample_power/ratio
    total_photon = ((total_power*t)/(h*c)) * (mono_wl*1e-9)
    
    # get only the metadata
    f = open(sig_path)
    Lines = f.readlines()
    metadata = Lines[:start]
    
    # build new power corrected data
    sig = read_xy(sig_path,start)
    x = sig[0]
    y = np.divide(sig[1],total_photon)
    
    new_sig = np.stack((x, y))
    
    
    plt.plot(new_sig[0],new_sig[1],color='darkred')
    plt.xlabel(r'Wavelength [$nm$]')
    plt.ylabel('Photon per photon count')
    plt.grid('on')
    plt.title(rf'Power corrected signal using: {pow_id}')
    
    return metadata, new_sig
    


"""
takes an exposure of the baseline electronic noise, given an exposure time and spectrometer wavelength and grating
"""
def take_baseline(folder_path,t,spec_wl,spec_gr):
    
    print('Making sure shutters are closed...')
    s.spectro.shutter = "closed"
    s.source_shutter.on = False
    print(rf'Setting exposure time to {t} seconds')
    s.spectro.exposure = t
    print(rf'Setting spectrometer wavelength to {spec_wl}nm')
    s.spectro.wavelength = spec_wl
    print(rf'Setting spectrometer grating to {spec_gr}')
    s.spectro.grating = spec_gr
    
    now = date_id()
    baseline_id = rf'BL_{now}_{t}sec_{spec_wl}wl_{spec_gr}gr'

    temp_path = os.path.join(folder_path,'temp.txt')
    save_path = os.path.join(folder_path,rf'{baseline_id}.txt')
    
    print('Taking exposure...')
    s.spectro.running  = True
    s.spectro.save_path = temp_path
    s.spectro.saved = True
    
    data = gather_metadata(baseline=True)
    make_standard(temp_path,data,save_path)
    
    return save_path



"""
fourth order polynomial
"""
def poly4(x,a,b,c,d,e):
    return a*x**4 + b*x**3 + c*x**2 + d*x + e



"""
second order polynomial
"""
def poly2(x,a,b,c):
    return a*x**2 + b*x + c

"""
analyses a baseline measurement signal and returns a fourth order best fit polynomial
"""
def analyse_baseline(bl_path):
    
    x,y = read_xy(bl_path,start)
    pixel_array = np.arange(0,1600,1)
    
    fit = np.polyfit(pixel_array,y,2)
    
    plt.scatter(pixel_array,y,s=2,color='red')
    plt.plot(pixel_array,poly2(pixel_array,fit[0],fit[1],fit[2]),color='darkred')
    plt.xlabel('Pixel')
    plt.ylabel('Photon Count')
    plt.grid('on')
    
    return fit