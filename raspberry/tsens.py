#!/usr/bin/python

import time


def gettem():
    temfile = open("/sys/bus/w1/devices/28-0315543db8ff/w1_slave")
    temtext = temfile.read()
    temfile.close()
    temdata = temtext.split("\n")[1].split(" ")[9]
    temperature = float(temdata[2:])
    temperature = temperature / 1000
    return temperature



while 1:
    print gettem()
    time.sleep(1)
 

