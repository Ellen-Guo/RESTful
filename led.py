import time
import RPi.GPIO as GPIO

# use default flask port
# broadcast list of IP address, port, and supported LED colors through zeroconf advertising
# must support and advertise the following colors: red, blue, green, magenta, cyan, yellow, white
# must use pulse width modulation for LED dimming
# status and color of LED obtained through GET request
# status and color of LED changed through POST request

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
LEDS = (27, 13, 26)
GPIO.setup(LEDS, GPIO.OUT)
GPIO.output(LEDS, False)

pwm = GPIO.PWM(LEDS, 50)  # frequency=50Hz
pwm.start(0)

# set intensity
intensity = # whatever from command
p.ChangeDutyCycle(intensity)

# set color
color = # whatever from command

status = # whatever from command
if status == 'on':
    if color == 'white':
        GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
    elif color == 'red':
        GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.LOW))
    elif color == 'blue':
        GPIO.output(LEDS, (GPIO.LOW, GPIO.LOW, GPIO.HIGH))
    elif colot == 'green':
        GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.LOW))
    elif color == 'magenta':
        GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.HIGH))
    elif colot == 'cyan':
        GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
    elif color == 'yellow':
        GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
    time.sleep(1)
else:
    GPIO.output(LEDS, False)

# Reset pins
pwm.stop()
GPIO.cleanup()