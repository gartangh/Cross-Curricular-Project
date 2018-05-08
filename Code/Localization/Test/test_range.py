#!/usr/bin/env python

import time
import numpy as np
import serial
import syslog
import time, sys, math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pypozyx import *

if __name__ == "__main__":

    # Variables and containers
    fig = str(os.path.join(".","Figures","test_ranging_" + time.strftime("%Y%m%d-%H%M%S") + ".png"))
    figdetail = str(os.path.join(".","Figures","test_ranging_" + time.strftime("%Y%m%d-%H%M%S") + "_detail.png"))

    timer = 1 # s
    smoother = 5 # amount of values
    speed_limit = 40 * 1000000 / 3600 # max speed of the object (mm/s)

    anchor = 0x6038 # anchor-id
    x = [] # time (s)
    y = [] # distance (mm)
    device_range = DeviceRange()

    smooth_x = [] # time (s)
    smooth_y = [] # distance (mm)

    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print "No Pozyx connected. Check your USB cable or your driver!" 
        quit()
        
    pozyx = PozyxSerial(serial_port)
#    pozyx.setRangingProtocol(POZYX_RANGE_PROTOCOL_PRECISION)

    # Ranging for 'timer' seconds
    start = time.time()
    i = 0
    while time.time()-start < timer:
        status = pozyx.doRanging(anchor,device_range)
        
        if status == POZYX_SUCCESS:
            dist = int(device_range.distance)
            t = time.time()-start
            x.append(t)
            y.append(dist)

            # Lower impossible peaks
            if i != 0:
                if abs(y[i] - y[i-1]) > speed_limit * (x[i] - x[i-1]):
                    if y[i] > y[i-1]:
                        y[i] = y[i-1] + speed_limit * (x[i] - x[i-1])
                    else:
                        y[i] = y[i-1] - speed_limit * (x[i] - x[i-1])

            # Smoother
            if i % smoother == (smoother - 1):
                smooth_x.append(t)
                smooth_y.append(np.mean(y[-smoother:]))

            i += 1

    # Statistic calculations and plotting
    plt.plot(x,y,'g-', markersize = 1, label='Afstanden') # ranges

    mean = np.mean(y)
    plt.axhline(y=mean,xmin=0,xmax=timer,c='b', label='Gemiddelde') # mean line
    plt.axhspan(mean-10, mean+10, color='y', alpha=0.5, lw=0, label='Afwijking kleinder dan 1 cm') 

    plt.axhspan(mean+10, mean+20, color='y', alpha=0.4, lw=0, label='Afwijking kleinder dan 2 cm')
    plt.axhspan(mean-10, mean-20, color='y', alpha=0.4, lw=0)

    plt.axhspan(mean+20, mean+30, color='y', alpha=0.3, lw=0, label='Afwijking kleinder dan 3 cm')
    plt.axhspan(mean-20, mean-30, color='y', alpha=0.3, lw=0)

    plt.axhspan(mean+30, mean+40, color='y', alpha=0.2, lw=0, label='Afwijking kleinder dan 4 cm')
    plt.axhspan(mean-30, mean-40, color='y', alpha=0.2, lw=0)

    plt.axhspan(mean+40, mean+50, color='y', alpha=0.1, lw=0, label='Afwijking kleinder dan 5 cm')
    plt.axhspan(mean-40, mean-50, color='y', alpha=0.1, lw=0)

    plt.plot(smooth_x,smooth_y,'r-', markersize = 1, label='Uitgemiddelde afstanden')

    plt.suptitle('Ranging without moving for ' + str(timer) + ' s')
    plt.xlabel('time (s)')
    plt.ylabel('distance (mm)')
    plt.axis((0,timer,np.min(y)-10,np.max(y)+10))
    plt.savefig(figdetail)
    plt.axis((0,timer,0,np.max(y)+100))
    plt.savefig(fig)
    plt.clf()
    plt.close()

    print '==============================================='
    print 'STATS'
    tags = 3
    print 'MEAN = ' + str(mean)
    print 'VAR = ' + str(np.var(y))
    print 'STD = ' + str(np.std(y))
    print 'FREQUENCY = ' + str(len(y)/timer)
    print 'FREQUENCY POS = ' + str(len(y)/timer/tags)
    print 'TIME/RANGE = ' + str(float(timer)/float(len(y)))
    print 'TIME/POSITON = ' + str(float(timer)/float(len(y))*tags)
    print '-----------------------------------------------'
    print 'TIME TO START SMOOTHER ' + str(np.min(smooth_x))
    print 'FREQUENCY SMOOTH = ' + str(len(smooth_y)/timer)
    print 'FREQUENCY POS SMOOTH = ' + str(len(smooth_y)/timer/tags)
    print 'TIME/RANGE SMOOTH= ' + str(float(timer)/float(len(smooth_y)))
    print 'TIME/POSITON SMOOTH = ' + str(float(timer)/float(len(smooth_y))*tags)
    print '==============================================='


