# lighting for the labyrinth

from __future__ import division
import threading
import time

import Adafruit_PCA9685
import random

# light[ ring, wall ] contains (pwm, channel) for each light
# note that (ring, wall) is really the polar coordinate
numrings = 5
numwalls = 4
#walls are numbered 0..4 from E-N-W-S

light = [
    [ (0,0), (0,1), (0,2), (0,3) ],
    [ (0,4), (0,5), (0,6), (0,7) ],
    [ (0,8), (0,9), (0,10), (0,11) ],
    [ (0,12), (0,13), (0,14), (0,15) ],
    [ (1,0), (1,1), (1,2), (1,3) ]
    ]

northsouth = [ (4,1), (3,1), (2,1), (1,1), (0,1),
               (0,3), (1,3), (2,3), (3,3), (4,3)
               ]
eastwest = [ (4,0), (3,0), (2,0), (1,0), (0,0),
             (0,2), (1,2), (2,2), (3,2), (4,2)
             ]


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = []
pwm.append(Adafruit_PCA9685.PCA9685(address=0x40))
##pwm.append(Adafruit_PCA9685.PCA9685(address=0x41))


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

class lightThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.run_lights = False
        self.step = 64

    def run(self):
        self.run_lights =  True
        print('Running LEDs, press Ctrl-C to quit...')
        x = 0
        curside = 0
        while self.run_lights:

            numsides = 4
            w = 0.001
            for i in range(0,4095,self.step):
                pwm[0].set_pwm(0,0,4095-i)
##                pwm[1].set_pwm(0,0,4095-i)
                pwm[0].set_pwm(7,0,i)

##                for side in range(4,8):
##                    pwm[1].set_pwm(side,0,i)
                #time.sleep(w)
            for i in range(4095,0,-self.step):
                pwm[0].set_pwm(0,0,4095-i)
##                pwm[1].set_pwm(0,0,4095-i)
                pwm[0].set_pwm(7,0,i)
##                for side in range(4,8):
##                    pwm[1].set_pwm(side,0,i)

    def stop(self):
        self.run_lights = False

if __name__ == '__main__':

    lt = lightThread()
    lt.start()

    for step in [8,16,32,64,128,256]:

        lt.step = step
        time.sleep(10)


        
