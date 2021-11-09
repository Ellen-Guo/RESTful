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

# white
GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
# red
GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.LOW))
# blue
GPIO.output(LEDS, (GPIO.LOW, GPIO.LOW, GPIO.HIGH))
# green
GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.LOW))
# magenta
GPIO.output(LEDS, (GPIO.HIGH, GPIO.LOW, GPIO.HIGH))
# cyan
GPIO.output(LEDS, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
# yellow
GPIO.output(LEDS, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW))

# how to brighten/dim an LED
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50)  # channel=12 frequency=50Hz
p.start(0)
try:
    while 1:
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
p.stop()

# Reset pins
GPIO.cleanup()