from machine import Pin, UART
import time
import json
import gc

from esp8266 import ESP8266
from dht import DHT11, InvalidChecksum, InvalidPulseCount
import mq2

# Setup inboard led 
led = Pin(25,Pin.OUT)

# Get device_id
device_id = '-'.join(hex(b)[2:] for b in machine.unique_id())

# Create an ESP8266 Object
ssid = "Tewaha" #$_ bash
pwd = "Welcome@2020-" #Welcome123

esp01 = ESP8266(uartPort=0 ,baudRate=115200, txPin=(12), rxPin=(13))
esp8266_at_ver = None

print(f"Starting ESP module: {esp01.startUP()}",)
print(f"ESP echo test: {esp01.echoING()}")

# Print ESP8266 AT command version and SDK details
esp8266_at_ver = esp01.getVersion()
if(esp8266_at_ver != None):
    print(esp8266_at_ver)

# Set the current WiFi in SoftAP+STA
print(f"WiFi Current Mode: {esp01.setCurrentWiFiMode()}")

# List available wifis
#print(f"Available wifis: {esp01.getAvailableAPs()}")

# Connect with the WiFi
while (1):
    if "WIFI CONNECTED" in esp01.connectWiFi(ssid=ssid, pwd=pwd):
        print(f"ESP-01S connected to {ssid} wifi.")
        break;
    else:
        print("Trying to connect to the wifi.")
        time.sleep(2)

# Initialize DHT module
pin = Pin(0, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)

# Initialize GPS module
gpsModule = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
print(gpsModule)

buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""

def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime
    
    timeout = time.time() + 8 
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        parts = buff.split(',')
    
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                #print(buff)
                
                latitude = convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    latitude = -latitude
                longitude = convertToDegree(parts[4])
                if (parts[5] == 'W'):
                    longitude = "-" + longitude
                satellites = parts[7]
                GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                break
                
        if (time.time() > timeout):
            TIMEOUT = True
            break
        time.sleep(0.5)
        
def convertToDegree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)

# Wait 20 sec for sensors warmup (MQ-2)
time.sleep(20)

# Main loop
while(1):
    led.toggle()

    temperature = 0
    humidity = 0

    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        gas = mq2.gas_state()
    except (InvalidChecksum, InvalidPulseCount) as e:
        print(f"Error with DHT module: {e}")

    # GPS rotation
    getGPS(gpsModule)

    if(FIX_STATUS == True):
        FIX_STATUS = False
        
    if(TIMEOUT == True):
        TIMEOUT = False
        
        latitude = ""
        longitude = ""
        satellites = ""
        GPStime = ""

    # Going to do HTTP Get Operation with www.httpbin.org/ip, It return the IP address of the connected device
    # httpCode, httpRes = esp01.doHttpGet("www.httpbin.org","/ip","RaspberryPi-Pico", port=80)
    # print("------------- www.httpbin.org/ip Get Operation Result -----------------------")
    # print("HTTP Code:",httpCode)
    # print("HTTP Response:",httpRes)
    # print("-----------------------------------------------------------------------------\r\n\r\n")
    
    data_json = {
                    "device_id": device_id,
                    "temperature": temperature,
                    "humidity": humidity,
                    "mq135_gas" : gas["Status"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "satellites": satellites,
                    "gps_time": GPStime,
                    "free_memory": gc.mem_free(),
                    "created_at": str(time.localtime())
                }

    servhttpCode, httpRes = esp01.doHttpPost(
                                        host="192.168.1.6",
                                        path="/sc_api/add",
                                        content_type="application/json",
                                        content=json.dumps(data_json),
                                        port=8000
                                        )
    #print("HTTP Code:",httpCode)
    
    print(data_json)
    
    time.sleep(2)
    led.toggle()

