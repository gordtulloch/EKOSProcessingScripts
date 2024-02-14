#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################################################
#
# Name        : MCP.py
# Purpose     : The Master Control Program (nods to TRON) coordinates all activities for OBSY
# Author      : Gord Tulloch
# Date        : February 14 2024
# License     : GPL v3
# Dependencies: Tested with EKOS, don't know if it'll work with other imaging tools 
# Usage       : Run as a service
# TODO:
#
############################################################################################################
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import astropy.io.fits as pyfits
import warnings
from datetime import datetime
import pytz
import os.path
import codecs
import serial
import PyIndi
import numpy as np
import skimage.io
import time
import sys
import threading
import requests
import gobject
gobject.threads_init()

from dbus import glib
glib.init_threads()

import os
from pysolar.solar import *
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps      # Install pillow instead of PIL
from MCPFunctions import getRain, checkSun, mlCloudDetect, getWeather, obsyOpen, obsyClose

# Suppress warnings
warnings.filterwarnings("ignore")

############################################################################################################
# CONFIGURATION 
############################################################################################################
debug=True
homedir="/home/gtulloch/Projects/EKOSProcessingScripts"
weatherUSBPort 	= "/dev/ttyUSB0"
rainUSBPort 	= "/dev/ttyUSB1"
long=-97.1385
lat=49.8954
runMCP=True
obsyStates=["Open","Open Pending","Closed","Close Pending","SafeMode"]
PENDING=5

while runMCP:
	# If it's raining or daytime, immediate shut down and wait 5 mins
	if getRain() or checkSun():
		obsyState = "Closed"
		obsyClose()
		time.sleep(300)
		continue

    # If weather looks unsuitable either stay closed or move to Close Pending if Open
	if mlCloudDetect() or getWeather():
		if obsyState == "Closed":
			continue
		# If Open give it PENDING minutes to change
		if obsyState == "Open":
			obsyState="Close Pending"
			pendingCount=1
		if obsyState == "Close Pending":
			pendingCount+=1
		if pendingCount == PENDING:
			obsyState="Closed"
			obsyClose()
			pendingCount=0
	else:
		# Good weather so set to Open Pending or Open
		if obsyState != "Open":
			obsyState="Open Pending"
			pendingCount=1
		if obsyState == "Open Pending":
			pendingCount=1
		if pendingCount==PENDING: 
			obsyState="Open"
			obsyOpen()
			pendingCount=0
    
	time.sleep(60)



