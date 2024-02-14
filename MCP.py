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
#
############################################################################################################

import logging
from MCPFunctions import getRain, checkSun, mlCloudDetect, getWeather, obsyOpen, obsyClose, ekos_dbus

############################################################################################################
# CONFIGURATION AND SETUP
############################################################################################################
debug			=	True
homedir			=	"/home/gtulloch/Projects/EKOSProcessingScripts/"
weatherUSBPort 	= 	"/dev/ttyUSB0"
rainUSBPort 	= 	"/dev/ttyUSB1"
long			=	-97.1385
lat				=	 49.8954
runMCP			=	True
maxPending		=	5
ekosProfile		=	"NTT8"
dbName			= 	homedir+"obsy.db"


# Suppress warnings
#warnings.filterwarnings("ignore")

# Set up Database
con = sqlite3.connect(dbName)
cur = con.cursor()

# Set up logging
logger = logging.getLogger('MCP.py')
logger.basicConfig(filename='MCP.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('MCP starting')

# Ensure Ekos is running or exit
ekosStartCounter=0
while not ekos_dbus.is_ekos_running():
	ekos_dbus.start_ekos()
	time.sleep(5)
	if ekosStartCounter > 5:
		logger.error('Unable to start Ekos')
		exit(1)

############################################################################################################
#                                    M  A  I  N  L  I  N  E 
############################################################################################################
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
		if pendingCount == maxPending:
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
		if pendingCount==maxPending: 
			obsyState="Open"
			obsyOpen()
			pendingCount=0
   
	logger.info('Obsy state is '+obsyState)
	time.sleep(60)

############################################################################################################
# SHUTDOWN
############################################################################################################
# Stop Ekos on the current computer
ekos_dbus.stop_ekos()

logger.info('Obsy closed')
cur.close()
con.close()
