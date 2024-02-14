############################################################################################################
# FUNCTIONS
############################################################################################################

############################################################################################################
# INDI Client Definition
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
    telescope_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    telescope_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(telescope_connect) # send this new value to the device

def obsyOpen():
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

    # Run the schedule
    # Create a session bus.
    #import dbus
    #bus = dbus.SessionBus()

    #remote_object = bus.get_object("org.kde.kstars", "/KStars/Ekos/Scheduler")
    #iface = dbus.Interface(remote_object, 'org.kde.kstars.Ekos.Scheduler')
    #iface.loadScheduler("/home/stellarmate/Pictures/daily.esl")

    return

def obsyClose():
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
    
    return

############################################################################################################
# Get cloud status from AllSkyCam
def mlCloudDetect():
   # Load the model
    model = load_model(homedir+"mlCloudDetect/keras_model.h5", compile=False)

    # Load the labels
    class_names = open(homedir+"mlCloudDetect/labels.txt", "r").readlines()

    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

	# Find the latest image in the allsky cam (created by external task) 
    image = Image.open(homedir+"mlCloudDetect/latest.jpg").convert("RGB")

	# resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

	# turn the image into a numpy array
    image_array = np.asarray(image)

	# Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

	# Load the image into the array
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    return class_name

############################################################################################################
# Check if the Sun is up
def checkSun():
    loc = coord.EarthLocation(long * u.deg, lat * u.deg)
    now = Time.now()
    altaz = coord.AltAz(location=loc, obstime=now)
    sun = coord.get_sun(now).transform_to(altaz)

    if (sun.alt.degree > -6.0):
        return True
    else:
        return False
        
############################################################################################################
# Get rain indicator from RG-11
def getRain():
    return

############################################################################################################
# Get local weather data from ADS-WS1
def getWeather():
    ser = serial.Serial(weatherUSBPort,2400,timeout=1)
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
    return