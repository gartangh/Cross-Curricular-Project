#!/usr/bin/env python

import math, time

from pypozyx import *
from drone_position import *

if __name__ == "__main__":
    optimus = DronePosition()
	
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    pozyx = PozyxSerial(serial_port)

    while True:
        pozyx.getEulerAngles_deg(optimus.euler)
	print str(optimus.euler)
	time.sleep(1)
