import time
import RPi.GPIO as GPIO

# use default flask port
# broadcast list of IP address, port, and supported LED colors through zeroconf advertising
# must support and advertise the following colors: red, blue, green, magenta, cyan, yellow, white
# must use pulse width modulation for LED dimming
# status and color of LED obtained through GET request
# status and color of LED changed through POST request

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

# parse get request
url = "http://x.x.x.x:port/LED?status=off&color=magenta&intensity=100"
posStatus = url.find("status=")
posStatusAnd = url.find("&", posStatus, posStatus + 11)
status = url[posStatus + 7: posStatusAnd]
posColor = url.find("color=")
posColorAnd = url.find("&", posColor, posColor + 14)
color = url[posColor + 6: posColorAnd]
posIntensity = url.find("intensity=")
intensity = url[posIntensity + 10:]

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
        time.sleep(5)
    else:
        GPIO.output(LEDS, False)
        time.sleep(5)