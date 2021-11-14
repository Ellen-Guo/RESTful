import time
import RPi.GPIO as GPIO
import argparse
import logging
import socket
from time import sleep
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from flask import Flask, request

# use default flask port
# broadcast list of IP address, port, and supported LED colors through zeroconf advertising
# must support and advertise the following colors: red, blue, green, magenta, cyan, yellow, white
# must use pulse width modulation for LED dimming
# status and color of LED obtained through GET request
# status and color of LED changed through POST request

app = Flask(__name__)


@app.route('/LED', methods=['GET'])
def LED():
    status = request.args.get('status')
    color = request.args.get('color')
    intensity = request.args.get('intensity')

    r = 27
    g = 13
    b = 26

    # Setup GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    LEDS = (r, g, b)
    GPIO.setup(LEDS, GPIO.OUT)
    GPIO.output(LEDS, False)

    pR = GPIO.PWM(r, 50)  # frequency=50Hz
    pG = GPIO.PWM(g, 50)  # frequency=50Hz
    pB = GPIO.PWM(b, 50)  # frequency=50Hz
    
    changeLED(intensity, color, status)
    
    def changeDC(iR, iG, iB):
        pR.start(iR)
        pG.start(iG)
        pB.start(iB)

    def changeLED(intensity, color, status):
        if status == 'on':
            if color == 'white':
                changeDC(intensity, intensity, intensity)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
            elif color == 'red':
                changeDC(intensity, 0, 0)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.LOW))
            elif color == 'blue':
                changeDC(0, 0, intensity)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.LOW, GPIO.HIGH))
            elif color == 'green':
                changeDC(0, intensity, 0)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.LOW))
            elif color == 'magenta':
                changeDC(intensity, 0, intensity)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.HIGH))
            elif color == 'cyan':
                changeDC(0, intensity, intensity)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
            elif color == 'yellow':
                changeDC(intensity, intensity, 0)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        else:
            pR.stop()
            pG.stop()
            pB.stop()
            GPIO.output(LEDS, False)
    
    
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()
    return "status: %s. Color: %s. Intensity: %s" % (status, color, intensity)


desc = {'Version': '1.0'}
local = socket.gethostbyname(socket.gethostname() + ".local")
print(local)
info = ServiceInfo(
    "_http._tcp.local.",
    "Testing._http._tcp.local.",
    addresses= [socket.inet_aton(local)], #Need IP address of LED pi. For testing on same device, use 0.0.0.0
    port=5000,
    properties=desc
#         server=socket.gethostname() + '.local.',
)

zeroconf = Zeroconf()
print("Registration of a service, press Ctrl-C to exit...")
zeroconf.register_service(info)


def signal_handler(signal, frame):
    print("Interrupt called")
    zeroconf.unregister_service(info)
    zeroconf.close()
    sys.exit(0)


if __name__ == '__main__':    
    app.run(host="0.0.0.0", port=5000, debug=True)
