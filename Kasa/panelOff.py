#!/usr/bin/python3
from KasaSmartPowerStrip import SmartPowerStrip
import time

power_strip = SmartPowerStrip('10.0.0.108')
print(power_strip.toggle_plug('off', plug_name='Flat Panel'))
time.sleep(5)
