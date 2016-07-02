# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685
import random

# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = []
pwm.append(Adafruit_PCA9685.PCA9685(address=0x40))
pwm.append(Adafruit_PCA9685.PCA9685(address=0x41))


# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm[0].set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm[0].set_pwm_freq(1000)

print('controlling LED on channel 0, press Ctrl-C to quit...')
x = 0
while True:
    #x = random.randint(0,4095)
##    x = (x+40)%4096
##    pwm.set_pwm(0, 0, x)
##    pwm.set_pwm(7, 0, 4095-x)
##    time.sleep(0.02)

    w = 0.01
    step = 16
    for i in range(0,4095,step):
        pwm[0].set_pwm(0,0,4095-i)
        pwm[1].set_pwm(0,0,4095-i)
        pwm[0].set_pwm(7,0,i)
        #time.sleep(w)
    for i in range(4095,0,-step):
        pwm[0].set_pwm(0,0,4095-i)
        pwm[1].set_pwm(0,0,4095-i)
        pwm[0].set_pwm(7,0,i)

        #time.sleep(w)
        
