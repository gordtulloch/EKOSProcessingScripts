#!/usr/bin/python3

from KasaSmartPowerStrip import SmartPowerStrip

power_strip = SmartPowerStrip('10.0.0.108')
maxAttempts=10

# get general system info
attempts=0
try:
    print(power_strip.get_system_info())
except:
    print("Timeout")
    if (attempts == maxAttempts):
        print("Too many timeouts exiting")
        exit(1)
    else:
        attempts=attempts+1
