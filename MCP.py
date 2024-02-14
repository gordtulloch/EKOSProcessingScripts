#!/usr/bin/env python3
import requests
import json
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import warnings
from datetime import datetime
import pytz
import os.path
import codecs, threading, sys, requests, time, json
import numpy as np
import serial

# Load in the old roof status so we can see if it changes
#f = open('roofstatus.json')

# returns JSON object as
# a dictionary
#oldRoofStatus = json.load(f)

# Suppress warnings
warnings.filterwarnings("ignore")

# ---------------{ CONFIGURATION }---------------
debug=True
com_port = "/dev/ttyUSB0"

# Location
long=-97.1385
lat=49.8954

# At what difference between the dewpoint and temp should we set the dew heater on?
DEWDIFF=9

# Get local weather data from ADS-WS1
ser = serial.Serial(com_port,2400,timeout=1)
ser.flush()
packet=ser.readline()
header = packet[0:2]
eom = packet[50:55]
if header == b"!!" and eom == b"\r\n":
	if (debug):
		print("===================================")
		print("Packet:")
		print(packet)
		print("Data:")
		print("Wind Speed                 : "+str(int(codecs.decode(packet[2:6], 'UTF-8'), 16))) # Wind Speed (0.1 kph)
		print("Wind Direction             : "+str(int(codecs.decode(packet[6:10], 'UTF-8'), 16))) # Wind Direction (0-255)
		print("Outdoor temp (0.1F)        : "+str(int(codecs.decode(packet[10:14], 'UTF-8'), 16))) # Outdoor Temp (0.1 deg F)
		print("Rain (0.1in)               : "+str(int(codecs.decode(packet[14:18], 'UTF-8'), 16))) # Rain* Long Term Total (0.01 inches)
		print("Barometer (0.1mbar)        : "+str(int(codecs.decode(packet[18:22], 'UTF-8'), 16))) # Barometer (0.1 mbar)
		print("Indoor Temp                : "+str(round((int(codecs.decode(packet[22:26], 'UTF-8'), 16)/10-32)/1.8,2))) # Indoor Temp (deg F)
		print("Outdoor humidity (0.1%)    : "+str(int(codecs.decode(packet[26:30], 'UTF-8'), 16))) # Outdoor Humidity (0.1%)
		print("Indoor Humidity (0.1%)     : "+str(int(codecs.decode(packet[30:34], 'UTF-8'), 16))) # Indoor Humidity (0.1%)
		print("Date (day of year)         : "+str(int(codecs.decode(packet[34:38], 'UTF-8'), 16))) # Date (day of year)
		print("Time (minute of day)       : "+str(int(codecs.decode(packet[38:42], 'UTF-8'), 16))) # Time (minute of day)
		print("Today's Rain Total (0.01in): "+str(int(codecs.decode(packet[42:46], 'UTF-8'), 16))) # Today's Rain Total (0.01 inches)*
		print("1Min Wind SPeed Average    : "+str(int(codecs.decode(packet[46:50], 'UTF-8'), 16))) # 1 Minute Wind Speed Average (0.1kph)*
		print("====================================")
		print(" ")
		
	# Wind Speed Calculations
	wind_speed = int(codecs.decode(packet[2:6], 'UTF-8'), 16)
	wind_speed = (wind_speed / 10)
	wind_speed = (wind_speed / 1.609344)
	wind_speed = round(wind_speed , 1)
	wx_wind_speed = wind_speed
		
	# Average Wind Speed Calculations
	average_wind_speed = int(codecs.decode(packet[46:50], 'UTF-8'), 16)
	average_wind_speed = (average_wind_speed / 10)
	average_wind_speed = (average_wind_speed / 1.609344)
	average_wind_speed = round(average_wind_speed , 1)
	wx_average_wind_speed = average_wind_speed
	
	# Wind Bearing Calculations
	x = int(codecs.decode(packet[6:10], 'UTF-8'), 16)
	y = ((int(x) / 255.0) * 360)
	wind_bearing = round(y)
	wx_wind_bearing = wind_bearing
	y = None
	
	# Wind Direction Calculations
	compass_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
	compass_lookup = round(wind_bearing / 45)
	wind_direction = compass_brackets[compass_lookup]
	wx_wind_heading = wind_direction
	
	# Barometer Calculations
	barometer = int(codecs.decode(packet[18:22], 'UTF-8'), 16)
	barometer_mbar = (barometer / 10)
	barometer_inhg = (barometer_mbar / 33.8639)
	barometer_inhg = round(barometer_inhg, 2)
	wx_barometer = barometer_inhg
	
	# Temperature Calculations
	temperature = int(codecs.decode(packet[22:26], 'UTF-8'), 16)
	temperature = (temperature / 10)
	wx_temperature = temperature
	wx_temperature_celsius = round((wx_temperature - 32) / 1.8, 2)
	
	# Humidity Calculations
	humidity = int(codecs.decode(packet[26:30], 'UTF-8'), 16)
	humidity = (humidity / 10)
	wx_humidity = humidity
		
	# Dewpoint Calculations
	T = wx_temperature_celsius
	RH = wx_humidity
	a = 17.271
	b = 237.7
	def dewpoint_approximation(T,RH):
		Td = (b * gamma(T,RH)) / (a - gamma(T,RH))
		return Td
	def gamma(T,RH):
		g = (a * T / (b + T)) + np.log(RH/100.0)
		return g
	Td = dewpoint_approximation(T,RH)
	DewPoint = 9.0/5.0 * Td + 32
	wx_dewpoint = round(DewPoint + 0.01, 2)

	# Total Rain Calculations
	total_rain = int(codecs.decode(packet[14:18], 'UTF-8'), 16)
	total_rain = (total_rain / 100)
	wx_total_rain = total_rain
	wx_total_rain_mm = total_rain / 24.5
	
	# Today Rain Calculations
	today_rain = int(codecs.decode(packet[42:46], 'UTF-8'), 16)
	today_rain = (today_rain / 100)
	wx_today_rain = today_rain
	wx_today_rain_mm = today_rain / 24.5
		
	now = datetime.now()
	now_utc = datetime.utcnow()
	timestamp2 = now.strftime("%Y-%m-%dT%H:%M:%S")
	timestamp_utc = now_utc.strftime("%Y-%m-%dT%H:%M:%S")
	timestamp_unix = str(int(time.time()))
else:
	print("No data")
	exit(1)

# Read the clouds.txt file and if cloudy close
f=open("clouds.txt","r")
cloudsStr=f.read()
if "Cloudy" in cloudsStr:
  roofOpenCode=0
  roofOpenReason="Current conditions are Cloudy"
  cloudPercent=100
else:
  roofOpenCode=1
  roofOpenReason="Current conditions are Not Cloudy"
  cloudPercent=0

if (wx_wind_speed > 10) and (wx_average_wind_speed > 15):
  roofOpenCode=0
  roofOpenReason="Current conditions are poor wind"+str(windSpeed)+"km/h"

# Is it daytime? Never open the roof
loc = coord.EarthLocation(long * u.deg, lat * u.deg)
now = Time.now()

altaz = coord.AltAz(location=loc, obstime=now)
sun = coord.get_sun(now).transform_to(altaz)

if (sun.alt.degree > 6.0):
  roofOpenCode=0
  roofOpenReason="Daytime"

# For future check a dewheaton file
if os.path.isfile("dewheaton.txt"):
  dewHeat="ON"
else:
  dewHeat="OFF"

# Write out a file for WeatherWatcher
f = open("/usr/local/share/indi/scripts/weather.txt", "w")
f.write("clouds="+str(cloudPercent)+"%\n")
f.write("temp="+"{:.2f}".format(wx_temperature_celsius)+"\n")
f.write("wind="+str(wx_wind_speed)+"\n")
f.write("gust="+str(wx_average_wind_speed)+"\n")
f.write("humidity="+str(wx_humidity)+"\n")
f.write("rain="+str(wx_today_rain_mm)+"\n")
f.write("light=0"+"\n")
f.write("switch=0"+"\n")
f.close()

# Email Gord if the roof open status changes
#if ((roofOpenCode == 1) and (oldRoofStatus.roof_status==0)):
#  sendmail("gord.tulloch@gmail.com","SPAO-OBS Roof Opened","SPAO-OBS Roof Opened","SPAO-OBS Roof Opened")
# print(oldRoofStatus["roof_status"]["open_ok"][0])

# Save and print the roof status
# Create a Python object (dict):
now               = datetime.now(pytz.utc)
obsTimeUtc        = now.strftime("%d/%m/%Y %H:%M:%S")
roofstatusObj = {
  "timestamp_utc": obsTimeUtc,
  "roof_status": {
        "open_ok": roofOpenCode,
        "reasons": roofOpenReason
    }
}

roofStatus = json.dumps(roofstatusObj)
print(roofStatus)

# Write json to file for next run
#f = open("/usr/local/share/indi/scripts/roofstatus.json", "w")
#json.dump(roofStatus,f)
#f.close()

