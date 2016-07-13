# lighting for the labyrinth
#
# todo:
#7/3/16: strip out queue and make sure basic loop works with Process
#Thread may be OK - need to test both with flask
#7/4/16: set up queuemanager as a separate thread owned by the lights object
#7/5/16: create lightmgr and lightrunner classes to separate command management
#   and light hardware updating (runner)


from __future__ import division
from threading import Thread
import multiprocessing as mp
import Queue
import time
from multiprocessing.managers import BaseManager


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



# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)



class Lights(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill = False
        self.run_lights = False
        self.step = 64
        self.cmd = None
        self.pwm = []
        self.pwm.append(Adafruit_PCA9685.PCA9685(address=0x40))
        ##pwm.append(Adafruit_PCA9685.PCA9685(address=0x41))
        self.pwm[0].set_pwm_freq(1000)
        
        class QueueManager(BaseManager):pass
        QueueManager.register('get_queue')
        self.qmgr = QueueManager(address=('127.0.0.1',50001),authkey='labyrinth')
        self.qmgr.connect()
        self.q = self.qmgr.get_queue()

    def checkq(self):
        if self.q and not self.q.empty():
            curq = self.q.get()
            if 'cmd' in curq:
                self.cmd = curq['cmd']
            print "received: ", curq
            if self.cmd == 'step':
                if 'value' in curq:
                    lt.step = curq['value']
            elif self.cmd == 'stop':
                self.run_lights = False
            elif self.cmd == 'start':
                self.run_lights = True
            elif self.cmd == 'kill':
                self.kill = True
            return curq
        else: 
            return None

    def run(self):
        self.run_lights =  True
        print('Running LEDs, press Ctrl-C to quit...')
        x = 0
        curside = 0
        while not self.kill:
            if self.checkq():
                next
            if self.run_lights:

                numsides = 4
                w = 0.01
                for i in range(0,4095,self.step):
                    self.pwm[0].set_pwm(0,0,4095-i)
    ##                pwm[1].set_pwm(0,0,4095-i)
                    self.pwm[0].set_pwm(7,0,i)

    ##                for side in range(4,8):
    ##                    self.pwm[1].set_pwm(side,0,i)
                    #time.sleep(w)
                for i in range(4095,0,-self.step):
                    self.pwm[0].set_pwm(0,0,4095-i)
    ##                self.pwm[1].set_pwm(0,0,4095-i)
                    self.pwm[0].set_pwm(7,0,i)
    ##                for side in range(4,8):
    ##                    self.pwm[1].set_pwm(side,0,i)
                    #time.sleep(w)

    def stop(self):
        self.run_lights = False

    def kill(self):
        self.kill = True
    

if __name__ == '__main__':



    lt = Lights()
    lt.start()

    for step in [8,16,32,64,128,256]:
        print "step is ", step
        lt.q.put({"cmd":"step","value":step})
        #lt.step = step
        time.sleep(30)

    #lt.stop()
    lt.q.put({'cmd':'stop'})

    


        
