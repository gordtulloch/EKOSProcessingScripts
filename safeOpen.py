#!venv/bin/python
# -*- coding: utf-8 -*-
import PyIndi
import numpy as np
import skimage.io
import cv2
import time
import sys
import threading
import astropy.io.fits as pyfits
import datetime
import requests

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

#############################################################################################################
## S E R V E R  S E T U P                                                                                  ##
#############################################################################################################
# connect the server
indiclient=IndiClient()
indiclient.setServer("10.0.0.173",7624)

if (not(indiclient.connectServer())):
     print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort()))
     sys.exit(1)

#############################################################################################################
## T E L E S C O P E  S E T U P                                                                            ##
#############################################################################################################
# connect the scope
telescope="EQMod Mount"
device_telescope=None
telescope_connect=None

# get the telescope device
device_telescope=indiclient.getDevice(telescope)
while not(device_telescope):
    time.sleep(0.5)
    device_telescope=indiclient.getDevice(telescope)

# wait CONNECTION property be defined for telescope
telescope_connect=device_telescope.getSwitch("CONNECTION")
while not(telescope_connect):
    time.sleep(0.5)
    telescope_connect=device_telescope.getSwitch("CONNECTION")

# if the telescope device is not connected, we do connect it
if not(device_telescope.isConnected()):
    # Property vectors are mapped to iterable Python objects
    # Hence we can access each element of the vector using Python indexing
    # each element of the "CONNECTION" vector is a ISwitch
    telescope_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    telescope_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(telescope_connect) # send this new value to the device

# Park the scope
telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")
while not(telescope_parkstatus):
    time.sleep(0.5)
    telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")

telescope_parkstatus[0].s=PyIndi.ISS_ON   # the "PARK" switch
telescope_parkstatus[1].s=PyIndi.ISS_OFF  # the "UNPARKED" switch
indiclient.sendNewSwitch(telescope_parkstatus) # send this new value to the device

telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")
while not(telescope_parkstatus):
    time.sleep(0.5)
    telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")

# Wait til the scope is finished moving
while (telescope_parkstatus.getState()==PyIndi.IPS_BUSY):
    print("Scope Parking")
    time.sleep(2)

# Turn on the first relay
url = 'http://10.0.0.101/30000/01'
response = requests.get(url)
# Wait
time.sleep(1)
# Turn it off again
url = 'http://10.0.0.101/30000/00'
response = requests.get(url)

# Roof is open unpark scope
telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")
while not(telescope_parkstatus):
    time.sleep(0.5)
    telescope_parkstatus=device_telescope.getSwitch("TELESCOPE_PARK")

telescope_parkstatus[0].s=PyIndi.ISS_OFF   # the "PARK" switch
telescope_parkstatus[1].s=PyIndi.ISS_ON  # the "UNPARKED" switch
indiclient.sendNewSwitch(telescope_parkstatus) # send this new value to the device