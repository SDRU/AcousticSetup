# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 17:20:12 2022

@author: Sandora

This code collects acoustic waves from Spectrum data acquisition card M4i.44xx-x8

"""

from m4i import *
from pyspcm import *
import matplotlib.pyplot as plt
import datetime
import numpy as np
import traceback
import time

try:
    # add the location of the pyspcm header file manually if there is an issue
    header_dir = os.path.split(__file__)[0]

    if not header_dir in sys.path:
        log.info('M4i: adding header_dir %s to sys.path' % header_dir)
        sys.path.append(header_dir)
    import pyspcm
    import py_header.spcerr
except (ImportError, OSError):
    info_str = 'to use the M4i driver install the pyspcm module and the M4i libs'
    log.exception(info_str)
    raise ImportError(info_str)    


    
try:
    # Consult m4i.py for the settings
    
    # General settings
    sample_rate = MEGA(10)    
    enabled_channels = [0,1]
    nr_channels = len(enabled_channels)
    
    # Channel settings
    mV_range = 10000 # the output voltage will be divided by this value
    input_path = 0
    termination = 1
    coupling = 1
    compensation = None
    
    # Trigger settings
    nr_triggers = 10
    trig_mode = 1 # 1 pos edge
    trig_termination = 0
    level_high = 4000
    
    # Data settings
    segment = 10240*2 # length of the acoustic wave
    post_trigger = segment-1024*4 # manipulate this parameter to shift the acoustic wave compared to the trigger pulse
    save_file = 0 # 1 on, 0 off
    folder = 'C:/Users/BLOG/Desktop/Carlo Sandra/20220613 Tissue diff/'
    # filename_base = time.strftime("%Y%m%d-%H%M%S")
    filename_base = time.strftime("%Y%m%d-%H%M%S") + '-Meat_5Hz_450V_Hole6'
    
    
    # Laser parameters that will be saved in the file header
    
    # Bad Er:YAG #2
    # pulse_period = 1000 # ms
    # duty_cycle = 200 # us
    # header = f"Sampling rate \t {sample_rate} Hz \nChannels \t {enabled_channels}\nmV range for channels \t {mV_range}\nSegment \t {segment}\nPost-trigger \t {post_trigger}\nPulse period [ms] \t {pulse_period}\nDuty cycle [us] {duty_cycle}\n"
    
    # Ferda's Er:YAG
    pulse_length = 350 # us
    frequency = 5 # Hz
    voltage = 450  # V
    header = f"Sampling rate \t {sample_rate} Hz \nChannels \t {enabled_channels[0]}\nmV range for channels \t {mV_range}\nSegment \t {segment}\nPost-trigger \t {post_trigger}\nPulse length [us] \t {pulse_length}\nFrequency [Hz] {frequency}\nVoltage [V] {voltage}\n"
    



    
    m4 = M4i(name='M4i')
    m4.sample_rate(sample_rate)
    exact_sample_rate = m4.exact_sample_rate()
    
    m4.initialize_channels(channels=enabled_channels, mV_range=mV_range, input_path=input_path,
                            termination=termination, coupling=coupling, compensation=compensation, memsize=segment, pretrigger_memsize=segment/2,
                            lp_filter=None)
    
    m4.set_ext0_OR_trigger_settings(trig_mode,trig_termination,coupling,level_high)
    
    data = np.zeros([segment*nr_channels, nr_triggers])
    
    for i in range(nr_triggers):
        begin_time = datetime.datetime.now()
        
        data[:,i] = m4.single_trigger_acquisition(1000, segment, post_trigger)   
        # data[:,i] = m4.single_software_trigger_acquisition(mV_range, segment, post_trigger)  
        
        print(i)
        
        # time.sleep(1)
        end_time = datetime.datetime.now()
        print(end_time-begin_time)
        
        # fig=plt.plot(np.arange(0,segment*nr_channels)/sample_rate,data[:,i])
        # fig.clear()
    
    # Processing 
    Voltages = np.zeros([segment,nr_channels, nr_triggers])
    for trigger in range(nr_triggers):    
        for channel in range(nr_channels):
            for s in range(segment):
                Voltages[s,channel, trigger] = data[s*nr_channels + channel,trigger]
    
    # Plotting
    for pulse in [1,nr_triggers-1]:
        fig, axs = plt.subplots(nr_channels)
        for channel in range(nr_channels):
            axs[channel].plot(np.arange(0,segment)/sample_rate, Voltages[:, channel,pulse])
            axs[channel].set_title(f'Channel {enabled_channels[channel]}')
        plt.xlabel("Time (s)")
    
    m4.close()
    
    # Saving data
    if save_file == 1:
        # for trigger in range(nr_triggers):
            # filename = folder + filename_base + f'-trigger{trigger}'+'.txt'
            filename = folder + filename_base + '.txt'
            
            with open(filename,'a') as f:  
                f.write(header)
                # np.savetxt(f,Voltages[:,enabled_channels[0],trigger], delimiter='\t',fmt='%1.6e')
                np.savetxt(f,Voltages[:,enabled_channels[0],:], delimiter='\t',fmt='%1.6e')

     
    figm = plt.figure()            
    M = np.max(data,0)    
    plt.plot(M)
    
except Exception:
    traceback.print_exc()
    print("Random error")
    m4.close()