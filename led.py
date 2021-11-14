import RPi.GPIO as GPIO
import socket
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from flask import Flask, request

# use default flask port
# broadcast list of IP address, port, and supported LED colors through zeroconf advertising
# must support and advertise the following colors: red, blue, green, magenta, cyan, yellow, white
# must use pulse width modulation for LED dimming
# status and color of LED obtained through GET request
# status and color of LED changed through POST request

app = Flask(__name__)
global status, color, intensity
status = 'off'
color = ''
intensity = 0

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
        

@app.route('/LED', methods=['POST'])
def LED_post():
    global status, color, intensity
    status = request.args.get('status')
    
    if status == 'off':
        color = ''
        intensity = 0
        changeLED(int(intensity), color, status)
    else:
        color = request.args.get('color')
        intensity = request.args.get('intensity')
        changeLED(int(intensity), color, status)
        
    return "Updated to status: %s. Color: %s. Intensity: %s" % (status, color, intensity)

@app.route('/LED', methods=['GET'])
def LED_get():
    global status, color, intensity
    return "Current status: %s. Color: %s. Intensity: %s" % (status, color, intensity)

desc = {'Colors': 'white, red, green, blue, cyan, magenta, yellow'}
local = socket.gethostbyname(socket.gethostname() + ".local")

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