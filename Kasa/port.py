#!/usr/bin/python3

from KasaSmartPowerStrip import SmartPowerStrip
import getopt, sys, time

if (len(sys.argv)==0):
    Print("Usage: port [#] [state] where # is 1..6 and state is on or off")

if ((int(sys.argv[1])>6) or (int(sys.argv[1])<1)):
    Print("Invalid port number")

if (sys.argv[2] not in ("on","off")):
    Print("Invalid port state must be on or off")

power_strip = SmartPowerStrip('10.0.0.108')
print(power_strip.toggle_plug(sys.argv[2], plug_num=int(sys.argv[1])))
