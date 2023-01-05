##################
### MeasureRun ###
###  By Nadav  ### 
##################

""" This file contains the functions involved in measurements. """

# ---- Modules ---- #

# Devserve
from devserve.clients import SystemClient

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

#s = SystemClient.from_json_file("localhost", "D:3CS/CTRL/Server/dev_config.json")

# ------------------ #





# initialise system settings
def initialise(exp, slit,s):
    print("Initialising... this may take a minute.")
    print()
    s.source.power = 100
    s.source_shutter.control = "computer"
    s.source_shutter.on = False
    s.flipper.position = "down"
    s.flipperB.position = "down"
    s.spectro.shutter = "closed"
    s.spectro.exposure = exp
    s.spectro.slit_width = slit
    print("Setup initialised.")
    print()




    

# excitation rules. take in a wavelength (of the monochromator) and returns the
# required state of the system: filter wheels, gratings.
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






# gets the system to a predefined initial state
def zero_system(s):
    s.source_shutter.control = "computer"
    s.source_shutter.on = False
    s.spectro.shutter = "closed"
    s.spfw.position = 6
    s.lpfw.position = 6
    s.lpfw2.position = 6
    s.flipper.position = "down"
    s.flipperB.position = 'down'
    s.horiba.gr = 0
    s.horiba.wl = 250
    print("System zeroed.")
    print(get_state(s))




    

# retrieves the state of the system
def get_state(s):
    shutter = s.source_shutter.on
    spectro_shutter = s.spectro.shutter
    mono_grating = s.horiba.gr
    mono_wl = s.horiba.wl
    spfw = s.spfw.position
    lpfw = s.lpfw.position
    lpfw2 = s.lpfw2.position
    flipper = s.flipper.position
    flipperB = s.flipperB.position

    return shutter, spectro_shutter, mono_grating, mono_wl, spfw, lpfw, lpfw2, flipper, flipperB






# saves a value to a file as a string    
def save_string(string,path,newline):
    file_path = path
    with open(file_path, 'a') as f:
        if newline == True:
            f.write(string)
            f.write('\n')
        else:
            f.write(string)



# fourth order polynomial
def poly4(x,a,b,c,d,e):
    return a*x**4 + b*x**3 + c*x**2 + d*x + e


# function that plots from spectrometer measurement
def signal_plot(path,startline,color):
    sig = open(path,'r')
    x = []
    y = []
    Lines = sig.readlines()

    size = len(Lines)
    for line in range(startline,size):
        x_val = float(Lines[line].split()[0])
        y_val = float(Lines[line].split()[1])

        x.append(x_val)
        y.append(y_val)

    plt.plot(x,y,color=color,label=path)
    plt.xlabel('Wavelength')
    plt.ylabel('Count')
    plt.legend()
    plt.grid("on")

    return x,y
            

# this function takes an array of exposure times and measures the electronic noise of the spectrometer
# twice, once for each grating.
def Noise_Run(t_exp,run,s):

    print("Starting Noise_Run()")
    print()

    # t_exp = array (e.g.: [1,2,5,10])
    # s          = the initiliased class
    # run = crystal run folder name
    # path = path to save raw data (usually electronic noise folder)

    now = str(datetime.now())
    b = re.split('-| |:|',now)

    # Saving information
    name = "Elec_Noise"
    savedir = rf"{name}_Run_{b[0]}{b[1]}{b[2]}{b[3]}{b[4]}"
    workdir = "DATA\\ElectronicNoise"
    path_to_save = rf"D:\\3CS\\{workdir}\\{savedir}"

    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)

    #make sure shutter is closed
    print("Making sure the spectro shutter is closed")
    print()
    s.spectro.shutter = "closed"
    s.spectro.slit_width = 1000

    # cycle thorugh 2 x t_exp runs of measurements
    grating = [1,2]
    meas_count = 0
    meas_tot = len(t_exp*4)
    for gr in grating:
        s.spectro.grating = gr
        for t in t_exp:
            print ("Measuring... "+str(round(meas_count/meas_tot,1)*100)+'%', end="\r")
            s.spectro.exposure = t
            s.spectro.running  = True
            meas_count+=1
            print ("Measuring... "+str(round(meas_count/meas_tot,1)*100)+'%', end="\r")
            filename = os.path.join(path_to_save,rf"{t}sec_{gr}gr_{name}.txt")
            s.spectro.save_path = filename
            s.spectro.saved = True
            meas_count+=1

    # create the dictionary that will hold the values of the polynomials
    noise_dict = {}

    print()

    # loop through the saved files and extract the arrays
    for gr in grating:
        for t in t_exp:
            filename = os.path.join(path_to_save,rf"{t}sec_{gr}gr_{name}.txt")
            file = open(filename,'r')
            Lines = file.readlines()
            x = []
            y = []    
            size = len(Lines)
            for line in range(32,size):
                val1 = float(Lines[line].split()[0])
                val2 = float(Lines[line].split()[1])
                x.append(val1)
                y.append(val2)

            # fit to 4th order polynomial
            fit = np.polyfit(x,y,4)

            # add to dictionary
            t_float = float(t)
            gr_int = int(gr)
            noise_dict[rf"{t_float}sec_{gr_int}gr"] = fit.tolist()

    print ("Measuring... 100%", end="\r")
    print("All done.")
    print()

    BGR_path = rf"D:\\3CS\\DATA\\_Scans_\\{run}\\BGR"
    if not os.path.exists(BGR_path):
        os.mkdir(BGR_path)

    
    #if not os.path.exists(path):
    noise_file_path = os.path.join(BGR_path,'noise_dict.txt')
    if not os.path.exists(noise_file_path):
        noise_file = open(noise_file_path, "x")
    
    with open(noise_file_path,'w') as f:
        f.write(json.dumps(noise_dict))
        

    return noise_dict




# a function that takes in a signal measurement and a noise dictionary measurement to subtract the noise from the signal.
# the noise dicitonary is an output of the function Noise_Run()
def Noise_Cancellation(sig_path,noise_dict_path,save_path):

    with open(noise_dict_path) as f:
        data = f.read()
    noise_dict = json.loads(data)

    sig = open(sig_path,'r')
    Lines = sig.readlines()


    t = float(Lines[18].split()[3])
    gr = int(Lines[9].split()[1])

    poly = noise_dict[rf'{t}sec_{gr}gr']
    
    a = poly[0]
    b = poly[1]
    c = poly[2]
    d = poly[3]
    e = poly[4]

    x_array = []
    y_array = []

    for line in range(42,len(Lines)):
        wl = float(Lines[line].split()[0])
        photon = float(Lines[line].split()[1])

        noise_point = poly4(wl,a,b,c,d,e)

        x_array.append(wl)
        y_array.append(photon - noise_point)


    if not os.path.exists(save_path):
        BGR = open(save_path, "x")

    with open(save_path, 'a') as f:
        for i in range(0,42):
            f.write(str(Lines[i]))      
        f.write('Path to raw measurement: '+sig_path)
        f.write('\n')
        f.write('Path to noise measurement: '+noise_dict_path)
        f.write('\n')
        f.write('\n')

    for i in range(len(x_array)):
        with open(save_path, 'a') as f:
            f.write(str(x_array[i]) + ' '+ str(y_array[i]))
            f.write('\n')

    

    return x_array,y_array




# this functions runs a full correlation study for the power meter correlations
# takes in the run ID and returns 
def Power_Run(s):

    path0 = 'D:\\3CS\\DATA\\PowerCorrelations'

    # Generate ID and create folder
    now = str(datetime.now())
    b = re.split('-| |:|',now)
    ID = rf"PowCorr_{b[0]}{b[1]}{b[2]}{b[3]}{b[4]}"

    folder_path = os.path.join(path0,rf'{ID}')

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    # zero the system
    #zero_system(s)

    min_wl = 250; max_wl = 800; num = 20;
    wl_vals = np.linspace(min_wl,max_wl,num)
    gratings = [0,1]

    for i in gratings:
        count = 0

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
        save = open(path, "x")

        # save metadata
        save_string('Date: '+str(datetime.now()),path,True)
        save_string('Grating: '+str(s.horiba.gr),path,True)
        save_string('',path,True)

        for wl in wl_vals:
            print(rf'{count}. Setting wavelength to: '+str(round(wl,1)))
            s.horiba.wl = round(wl,1)

            s.power_meter_a.wavelength = round(wl,1)
            s.power_meter_b.wavelength = round(wl,1)

            #get power reading
            print('Getting power...')
            power_read_a = s.power_meter_a.power
            power_read_b = s.power_meter_b.power

            #save measurement
            print('Saving ...')
            save_string(str(round(wl,1))+';',path,False)
            save_string(str(power_read_a)+';',path,False)
            save_string(str(power_read_b),path,True)

            count+=1
            print('Measurement saved successfully. Moving on to the next wavelength.')
            print()
            print()

    print('Processing data...')

    file_path0 = rf'D:/3CS/DATA/PowerCorrelations/{ID}/pow_gr{0}.txt'
    file_path1 = rf'D:/3CS/DATA/PowerCorrelations/{ID}/pow_gr{1}.txt'

    pmc0 = open(file_path0,'r')
    pmc1 = open(file_path1,'r')

    wl_array = []
    pm_a_0 = []
    pm_b_0 = []
    pm_a_1 = []
    pm_b_1 = []

    b_over_a0 = []
    b_over_a1 = []

    Lines0 = pmc0.readlines()
    Lines1 = pmc1.readlines()

    size = len(Lines0)
    for line in range(3,size):
        li0 =Lines0[line].split(';')
        li1 = Lines1[line].split(';')
        wl_array.append(float(li0[0]))
        pm_a_0.append(float(li0[1])*1e6)
        pm_b_0.append(float(li0[2])*1e6)
        pm_a_1.append(float(li1[1])*1e6)
        pm_b_1.append(float(li1[2])*1e6)
        
    for i in range(0,len(pm_a_0)):
        b_over_a0.append(pm_b_0[i]/pm_a_0[i])
        b_over_a1.append(pm_b_1[i]/pm_a_1[i])

    # calculate the best fit polynomials for A(B) (after sorting)

    x0 = np.array(pm_b_0)
    y0 = np.array(pm_a_0)
    sorted_indices = np.argsort(x0)
    x0 = x0[sorted_indices]
    y0 = y0[sorted_indices]

    x1 = np.array(pm_b_1)
    y1 = np.array(pm_a_1)
    sorted_indices = np.argsort(x1)
    x1 = x1[sorted_indices]
    y1 = y1[sorted_indices]
    
    AB0 = np.polyfit(x0,y0,4)
    AB1 = np.polyfit(x1,y1,4)

    # create A(B) file
    AB_path = os.path.join(folder_path,'AB.txt')
    AB = open(AB_path,'x')
    with open(AB_path,'w') as f:
        f.write(str(datetime.now()))
        f.write('\n')
        f.write('\n')
        f.write(str(AB0[0])+';' + str(AB0[1])+';'+ str(AB0[2])+';'+ str(AB0[3])+';'+ str(AB0[4]))
        f.write('\n')
        f.write(str(AB1[0])+';' + str(AB1[1])+';'+ str(AB1[2])+';'+ str(AB1[3])+';'+ str(AB1[4]))

    # generate A(B) plot

    A = AB0[0]
    B = AB0[1]
    C = AB0[2]
    D = AB0[3]
    E = AB0[4]
    
    y_array0 = []
    for b in x0:
        y_val = poly4(b,A,B,C,D,E)
        y_array0.append(y_val)

    A = AB1[0]
    B = AB1[1]
    C = AB1[2]
    D = AB1[3]
    E = AB1[4]

    y_array1 = []
    for b in x1:
        y_val = poly4(b,A,B,C,D,E)
        y_array1.append(y_val)

    plt.plot(x0,y_array0,color='darkgreen',label='grating 0')
    plt.plot(x1,y_array1,color='black',label='grating 1')
    plt.grid("on")
    plt.xlabel(r"B $[\mu W]$")
    plt.ylabel(r"A $[\mu W]$")
    plt.legend()
    plt.title(rf'A(B): {ID}')

    fig_path = os.path.join(folder_path,'AB_plot.png')
    plt.savefig(fig_path)
    plt.show()
        
 
    # calculate the best fit polynomials for the ratio
    fit0 = np.polyfit(wl_array,b_over_a0,4)
    fit1 = np.polyfit(wl_array,b_over_a1,4)

    # create the ratio file
    ratio_path = os.path.join(folder_path,'pow_ratio.txt')
    ratio = open(ratio_path,'x')
    with open(ratio_path,'w') as f:
        f.write(str(datetime.now()))
        f.write('\n')
        f.write('\n')
        f.write(str(fit0[0])+';' + str(fit0[1])+';'+ str(fit0[2])+';'+ str(fit0[3])+';'+ str(fit0[4]))
        f.write('\n')
        f.write(str(fit1[0])+';' + str(fit1[1])+';'+ str(fit1[2])+';'+ str(fit1[3])+';'+ str(fit1[4]))

    # generate ratio plot
    A = fit0[0]
    B = fit0[1]
    C = fit0[2]
    D = fit0[3]
    E = fit0[4]
    
    y_array0 = []
    for wl in wl_array:
        y_val = poly4(wl,A,B,C,D,E)
        y_array0.append(y_val)

    A = fit1[0]
    B = fit1[1]
    C = fit1[2]
    D = fit1[3]
    E = fit1[4]

    y_array1 = []
    for wl in wl_array:
        y_val = poly4(wl,A,B,C,D,E)
        y_array1.append(y_val)

    plt.plot(wl_array,y_array0,color='darkgreen',label='grating 0')
    plt.scatter(wl_array,b_over_a0,color='darkgreen',label='grating 0')
    plt.plot(wl_array,y_array1,color='black',label='grating 1')
    plt.scatter(wl_array,b_over_a1,color='black',label='grating 1')
    plt.grid("on")
    plt.xlabel(r"Incident wavelength $[nm]$")
    plt.ylabel("B/A")
    plt.legend()
    plt.title(rf'Power Meter Ratio: {ID}')

    fig_path = os.path.join(folder_path,'ratio_plot.png')
    plt.savefig(fig_path)

    # create the monochromator efficiency file
    eff_path = os.path.join(folder_path,'pow_eff.txt')
    eff = open(eff_path,'x')
    with open(eff_path,'w') as f:
        f.write(str(datetime.now()))
        f.write('\n')
        f.write('pm_A_gr0;pm_B_gr0;pm_A_gr1;pm_B_gr1')
        f.write('\n')
        for i in range(0,len(wl_array)):
            f.write(str(pm_a_0[i])+';'+str(pm_b_0[i])+';'+str(pm_a_1[i])+';'+str(pm_b_1[i]))
            f.write('\n')

    # generate efficiency plot
    plt.plot(wl_array,pm_a_0,label='Power Meter A: grating 0',color='red')
    plt.plot(wl_array,pm_b_0,label='Power Meter B: grating 0',color='red',linestyle='--')
    plt.plot(wl_array,pm_a_1,label='Power Meter A: grating 1',color='darkblue')
    plt.plot(wl_array,pm_b_1,label='Power Meter B: grating 1',color='darkblue',linestyle='--')
    plt.xlabel(r"Incident wavelength $[nm]$")
    plt.ylabel(r'Power $[\mu W]$')
    plt.legend()
    plt.title(rf'Monochromator efficiency {now}')
    plt.grid("on")

    fig_path = os.path.join(folder_path,'eff_plot.png')
    plt.savefig(fig_path)

    print('All Done.')

    
# returns a folder with the power corrected signal
def Power_Correction(sig_path,Pow_ID,save_path):
    Pow_path = rf'D:\3CS\DATA\PowerCorrelations\{Pow_ID}\pow_ratio.txt'

    # constants
    h = 6.62607015e-34
    c = 299792458

    # retrieve power sample, grating, exposure and exc. wl of signal
    sig = open(sig_path,'r')
    sig_lines = sig.readlines()
    power_sample = float(sig_lines[1].split()[1])*1e6
    grating = int(sig_lines[7].split()[1])
    t_exp = float(sig_lines[18].split()[3])
    exc_wl = float(sig_lines[8].split()[1])*1e-9

    # retrieve polynomial values of best fit from power run
    power = open(Pow_path,'r')
    power_lines = power.readlines()
    line = power_lines[2+grating].split(';')

    A = float(line[0])
    B = float(line[1])
    C = float(line[2])
    D = float(line[3])
    E = float(line[4])

    sample_fraction = poly4(exc_wl,A,B,C,D,E)
    power_total = power_sample/sample_fraction
    photon_total = (((power_total/1e6)*t_exp)/(h*c))*exc_wl

    # create file
    save = open(save_path,'x')
    with open(save_path,'w') as f:
        for line in range(0,45):
            f.write(sig_lines[line])

    # build corrected signal
    wl_array = []
    count_array = []
    for line in range(45,len(sig_lines)):
        wl_array.append(float(sig_lines[line].split()[0]))
        count_array.append(float(sig_lines[line].split()[1])/photon_total)

    with open(save_path,'a') as f:
        for i in range(0,len(sig_lines) - 46):
            f.write(str(wl_array[i])+' '+str(count_array[i]))
            f.write('\n')

    return power_sample, power_total, photon_total

    

    


    
