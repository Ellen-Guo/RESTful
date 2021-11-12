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
    return "status: %s. Color: %s. Intensity: %s" % (status, color, intensity)


desc = {'Version': '1.0'}
info = ServiceInfo(
    "_http._tcp.local.",
    "Testing._http._tcp.local.",
    addresses= [socket.inet_aton("0.0.0.0")], #Need IP address of LED pi. For testing on same device, use 0.0.0.0
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
    pR.start(0)
    pG = GPIO.PWM(g, 50)  # frequency=50Hz
    pG.start(0)
    pB = GPIO.PWM(b, 50)  # frequency=50Hz
    pB.start(0)
    
    changeLED(intensity, color, status)

    # Reset pins
    pR.stop()
    pG.stop()
    pB.stop()
    GPIO.cleanup()

    def changeLED(intensity, color, status):
        if status == 'on':
            if color == 'white':
                pR.ChangeDutyCycle(intensity)
                pG.ChangeDutyCycle(intensity)
                pB.ChangeDutyCycle(intensity)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
            elif color == 'red':
                pR.ChangeDutyCycle(intensity)
                pG.ChangeDutyCycle(0)
                pB.ChangeDutyCycle(0)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.LOW))
            elif color == 'blue':
                pR.ChangeDutyCycle(0)
                pG.ChangeDutyCycle(0)
                pB.ChangeDutyCycle(intensity)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.LOW, GPIO.HIGH))
            elif color == 'green':
                pR.ChangeDutyCycle(0)
                pG.ChangeDutyCycle(intensity)
                pB.ChangeDutyCycle(0)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.LOW))
            elif color == 'magenta':
                pR.ChangeDutyCycle(intensity)
                pG.ChangeDutyCycle(0)
                pB.ChangeDutyCycle(intensity)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.HIGH))
            elif color == 'cyan':
                pR.ChangeDutyCycle(0)
                pG.ChangeDutyCycle(intensity)
                pB.ChangeDutyCycle(intensity)
                GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
            elif color == 'yellow':
                pR.ChangeDutyCycle(intensity)
                pG.ChangeDutyCycle(intensity)
                pB.ChangeDutyCycle(0)
                GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        else:
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