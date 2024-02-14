#!/usr/bin/python3
from KasaSmartPowerStrip import SmartPowerStrip
import time

power_strip = SmartPowerStrip('10.0.0.108')
print(power_strip.toggle_plug('on', plug_name='Flat Panel'))

# Needs a few secs to fire up for some reason!
time.sleep(5)
