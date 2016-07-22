# lighting for the labyrinth
#
# todo:
#7/3/16: strip out queue and make sure basic loop works with Process
#Thread may be OK - need to test both with flask
#7/4/16: set up queuemanager as a separate thread owned by the lights object
#7/5/16: create lightmgr and lightrunner classes to separate command management
#   and light hardware updating (runner)


from __future__ import division
from __future__ import print_function
from threading import Thread
import multiprocessing as mp
import Queue
import time
from multiprocessing.managers import BaseManager


import Adafruit_PCA9685
import random

# lightpc[ ring, wall ] contains (pwm, channel) for each light
# note that (ring, wall) is really the polar coordinate
numrings = 5
numwalls = 4
#walls are numbered 0..4 from E-N-W-S

lightpc = [
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
class Walls():
    def __init__(self):
        self.pwm=[]
        self.channel=[]
        self.x=[]
        self.y=[]
        self.rho=[]
        self.theta=[]
        self.intensity=[]
        num_walls = 0

    def add_wall(self,pwm,channel,x,y,rho,theta,intensity=0):
        self.pwm.append(pwm)
        self.channel.append(channel)
        self.x.append(x)
        self.y.append(y)
        self.rho.append(rho)
        self.theta.append(theta)
        self.intensity.append(intensity)
        self.num_walls = len(self.pwm)

    def get_wall(self,i):
        return { 'pwm': self.pwm[i],
                 'channel': self.channel[i],
                 'x':self.x[i],
                 'y': self.y[i],
                 'rho': self.rho[i],
                 'theta':self.theta[i],
                 'intensity':self.intensity[i],
                 }


class Lights(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill = False
        self.run_lights = False
        self.step = 64
        self.minbright = 0
        self.maxbright = 4095
        self.cmd = None
        self.pwm = []
        self.pwm.append(Adafruit_PCA9685.PCA9685(address=0x40))
        self.pwm.append(Adafruit_PCA9685.PCA9685(address=0x41))
        for p in self.pwm:
            p.set_pwm_freq(60)

        self.walls = Walls()
        self.walls.add_wall( self.pwm[1], 3, 6, 5, 1, 0, 0 )
        self.walls.add_wall( self.pwm[1], 2, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[1], 1, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[1], 0, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[0], 15, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 14, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 13, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 12, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 11, 5, 6, 3, 1, 0 )
        self.walls.add_wall( self.pwm[0], 10, 5, 6, 3, 1, 0 )
        self.walls.add_wall( self.pwm[0], 9, 5, 6, 3, 1, 0 )
        self.walls.add_wall( self.pwm[0], 8, 5, 6, 3, 1, 0 )
        self.walls.add_wall( self.pwm[0], 7, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 6, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 5, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 4, 5, 6, 2, 1, 0 )
        self.walls.add_wall( self.pwm[0], 3, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[0], 2, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[0], 1, 5, 6, 1, 1, 0 )
        self.walls.add_wall( self.pwm[0], 0, 5, 6, 1, 1, 0 )


            
        
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
            print ("received: ", curq)
            if self.cmd == 'step':
                if 'value' in curq:
                    lt.step = curq['value']
            elif self.cmd == 'min':
                if 'value' in curq:
                    lt.minbright = int(curq['value']*4095)
                    if lt.minbright<0:
                        lt.minbright = 0
                    if lt.minbright > 4095:
                        lt.minbright = 4095
            elif self.cmd == 'max':
                if 'value' in curq:
                    lt.maxbright = int(curq['value']*4095)
                    if lt.maxbright<0:
                        lt.maxbright = 0
                    if lt.maxbright > 4095:
                        lt.maxbright = 4095

            elif self.cmd == 'stop':
                self.run_lights = False
            elif self.cmd == 'start':
                self.run_lights = True
            elif self.cmd == 'kill':
                self.kill = True
            elif self.cmd == 'off':
                for p in self.pwm:
                    p.set_all_pwm(0,0)
                self.run_lights = False
            return curq
        else: 
            return None

    def update_walls(self):
        for i in range(self.walls.num_walls):
            self.walls.pwm[i].set_pwm(self.walls.channel[i],
                                      0,self.walls.intensity[i])
                                      

    def run(self):
        self.run_lights =  True
        print('Running LEDs, press Ctrl-C to quit...')
        x = 0
        curside = 0
        cycletime = 5.0 #seconds
        starttime = time.time()
        numwalls = len(self.walls.pwm)
        while not self.kill:
            curtime = time.time()
            curstep = (curtime-starttime)/cycletime
            if curstep > 1.0 :
                starttime = curtime
                next
            
            if self.checkq():
                next
                
            if self.run_lights:

                for i in range(numwalls):
                    self.walls.intensity[i] = random.randint(self.minbright,self.maxbright)

                self.update_walls()
                
                w = 1.0
                time.sleep(w)

    def stop(self):
        self.run_lights = False

    def kill(self):
        self.kill = True
    

if __name__ == '__main__':



    lt = Lights()
    lt.start()

    for step in [8,16,32,64,128,256]:
#    for step in [64,128,256]:
        print("step is ", step)
        lt.q.put({"cmd":"step","value":step})
        #lt.step = step
        time.sleep(30)

    #lt.stop()
    #lt.q.put({'cmd':'stop'})
    print("ctrl-c to exit")
    while True:
        time.sleep(3)
        pass

    


        
