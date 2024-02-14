from KasaSmartPowerStrip import SmartPowerStrip
import time
from datetime import datetime
dt = datetime.now()

power_strip = SmartPowerStrip('10.0.0.108')
maxAttempts=10
f = open("/usr/local/share/indi/scripts/stripPowerLog.txt","a")
# get power usage info
for i in range(1,7):
    attempts=0
    while (attempts < maxAttempts):
        try:
            info=power_strip.get_realtime_energy_info(plug_num=i)
            # print("Port ",i," usage: ",info)
            break
        except:
            print("Timeout")
            if (attempts == maxAttempts):
                print("Too many timeouts exiting")
                exit(1)
            else:
                attempts=attempts+1
    f.write(dt.strftime("%d-%m-%Y, %H:%M:%S")+","+str(i)+","+str(info['slot_id'])+","+str(info['current_ma'])+","+str(info['voltage_mv'])+","+str(info['power_mw'])+","+str(info['total_wh'])+'\r\n')
f.close()
