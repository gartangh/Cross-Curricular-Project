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

heading = 50 # get from pozyx
ref = 0 # reference angle

start_x = 0
start_y = 0
stop_x = 100
stop_y = 100

calibration = heading - math.atan2(stop_y-start_y,stop_x-start_x)*180/math.pi # get from 2 coordinates
print "calibration = " + str(calibration)
# angle to the reference angle
def angle(h):

    if float(h) > 180:
        h -= 360.0

    return h-calibration

print "heading tov reference = " + str(angle(0))

if __name__ == "__main__":

    # Variables and containers
    fig = str(os.path.join(".","Figures","test_heading_" + time.strftime("%Y%m%d-%H%M%S") + ".png"))

    timer = 0 # s

    x = [] # time (s)
    y = [] # angle (mm)
    euler = EulerAngles()

    # Assign a serial port of the Pozyx
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print "No Pozyx connected. Check your USB cable or your driver!" 
        quit()
        
    pozyx = PozyxSerial(serial_port)

    # Ranging for 'timer' seconds
    start = time.time()
    i = 0
    while time.time()-start < timer:

        pozyx.getEulerAngles_deg(euler)
        print str(euler[0])

        i += 1