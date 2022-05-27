import uos
import machine
import utime
"""
Raspberry Pi Pico/MicroPython + ESP-01S exercise

ESP-01S(ESP8266) with AT-command firmware:
AT version:1.7.4.0(May 11 2020 19:13:04)

Pico send AT command to ESP-01S via UART,
- set in station mode
- join AP
- connect to server ip:port 9999
- send text and wait response
"""
#server port & ip hard-coded,
#have to match with server side setting
server_ip="192.168.4.1"
server_port=9999

print()
print("Machine: \t" + uos.uname()[4])
print("MicroPython: \t" + uos.uname()[3])

#indicate program started visually
led_onboard = machine.Pin(25, machine.Pin.OUT)
led_onboard.value(0)     # onboard LED OFF/ON for 0.5/1.0 sec
utime.sleep(0.5)
led_onboard.value(1)
utime.sleep(1.0)
led_onboard.value(0)

uart0 = machine.UART(0, baudrate=115200)
print(uart0)

def sendCMD_waitResp(cmd, uart=uart0, timeout=2000):
    print("CMD: " + cmd)
    uart.write(cmd)
    waitResp(uart, timeout)
    print()
    
def waitResp(uart=uart0, timeout=2000):
    prvMills = utime.ticks_ms()
    resp = b""
    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])
    print("resp:")
    try:
        print(resp.decode())
    except UnicodeError:
        print(resp)
        
# send CMD to uart,
# wait and show response without return
def sendCMD_waitAndShow(cmd, uart=uart0):
    print("CMD: " + cmd)
    uart.write(cmd)
    while True:
        print(uart.readline())
        
def espSend(text="test", uart=uart0):
    sendCMD_waitResp('AT+CIPSEND=' + str(len(text)) + '\r\n')
    sendCMD_waitResp(text)
        
def XmonitorESP(uart=uart0):
    """
    while True:
        line=uart.readline()
        try:
            print(line.decode())
        except UnicodeError:
            print(line)
    """
    while True:
        if uart.any():
            print(uart.read(1))
    
sendCMD_waitResp('AT\r\n')          #Test AT startup
sendCMD_waitResp('AT+GMR\r\n')      #Check version information
#sendCMD_waitResp('AT+RESTORE\r\n')  #Restore Factory Default Settings

sendCMD_waitResp('AT+CWMODE?\r\n')  #Query the Wi-Fi mode
sendCMD_waitResp('AT+CWMODE=1\r\n') #Set the Wi-Fi mode 1 = Station mode
#sendCMD_waitResp('AT+CWMODE=2\r\n') #Set the Wi-Fi mode 2 = S0ftAP mode
sendCMD_waitResp('AT+CWMODE?\r\n')  #Query the Wi-Fi mode again

#sendCMD_waitResp('AT+CWLAP\r\n', timeout=10000) #List available APs
sendCMD_waitResp('AT+CWJAP="ESP32-ssid","password"\r\n', timeout=5000) #Connect to AP
sendCMD_waitResp('AT+CIFSR\r\n')    #Obtain the Local IP Address
#sendCMD_waitResp('AT+CIPSTART="TCP","192.168.12.147",9999\r\n')
sendCMD_waitResp('AT+CIPSTART="TCP","' +
                 server_ip +
                 '",' +
                 str(server_port) +
                 '\r\n')
espSend()

while True:
    print('Enter something:')
    msg = input()
    #sendCMD_waitResp('AT+CIPSTART="TCP","192.168.12.147",9999\r\n')
    sendCMD_waitResp('AT+CIPSTART="TCP","' +
                 server_ip +
                 '",' +
                 str(server_port) +
                 '\r\n')
    espSend(msg)