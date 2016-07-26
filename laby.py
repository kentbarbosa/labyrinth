# lighting for the labyrinth
#
# todo:
#7/3/16: strip out queue and make sure basic loop works with Process
#Thread may be OK - need to test both with flask
#7/4/16: set up queuemanager as a separate thread owned by the lights object
#7/5/16: create lightmgr and lightrunner classes to separate command management
#   and light hardware updating (runner)
#7/23/2016: created Strands class to handle location, pwm, channel info
#           for each strand of lights
#       todo: need to set up status queue


from __future__ import division
from __future__ import print_function
from threading import Thread
import multiprocessing as mp
import Queue
import time
from multiprocessing.managers import BaseManager


import Adafruit_PCA9685
import random


class Strands():
    def __init__(self):
        self.pwm=[]
        self.channel=[]
        self.x=[]
        self.y=[]
        self.rho=[]
        self.theta=[]
        self.intensity=[]
        num_strands = 0

    def add_strand(self,pwm,channel,x,y,rho,theta,intensity=0):
        self.pwm.append(pwm)
        self.channel.append(channel)
        self.x.append(x)
        self.y.append(y)
        self.rho.append(rho)
        self.theta.append(theta)
        self.intensity.append(intensity)
        self.num_strands = len(self.pwm)

    def get_strand(self,i):
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
        self.cycle_time = 5.0 #seconds
        self.mincycle_time = 0.5
        self.maxcycle_time = 600.0
        self.step_time = 0.1
        self.minstep_time = 0.01
        self.maxstep_time = 600.0

        self.minbright = 0
        self.maxbright = 4095
        self.cmd = None
        self.pwm = []
        self.pwm.append(Adafruit_PCA9685.PCA9685(address=0x40))
        self.pwm.append(Adafruit_PCA9685.PCA9685(address=0x41))
        for p in self.pwm:
            p.set_pwm_freq(60)

        self.strands = Strands()
        self.strands.add_strand( self.pwm[1], 3, 6, 5, 1, 0, 0 )
        self.strands.add_strand( self.pwm[1], 2, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[1], 1, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[1], 0, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[0], 15, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 14, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 13, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 12, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 11, 5, 6, 3, 1, 0 )
        self.strands.add_strand( self.pwm[0], 10, 5, 6, 3, 1, 0 )
        self.strands.add_strand( self.pwm[0], 9, 5, 6, 3, 1, 0 )
        self.strands.add_strand( self.pwm[0], 8, 5, 6, 3, 1, 0 )
        self.strands.add_strand( self.pwm[0], 7, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 6, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 5, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 4, 5, 6, 2, 1, 0 )
        self.strands.add_strand( self.pwm[0], 3, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[0], 2, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[0], 1, 5, 6, 1, 1, 0 )
        self.strands.add_strand( self.pwm[0], 0, 5, 6, 1, 1, 0 )


            
        
        class QueueManager(BaseManager):pass
        QueueManager.register('get_queue')
        self.qmgr = QueueManager(address=('127.0.0.1',50001),authkey='labyrinth')
        self.qmgr.connect()
        self.q = self.qmgr.get_queue()

    def update_status(self):
        print('cycle_time: ',self.cycle_time)
        print('step_time: ',self.step_time)
        print('maxbright: ',self.maxbright)
        print('minbright: ',self.minbright)
        
        
    def checkq(self):
        if self.q and not self.q.empty():
            curq = self.q.get()
            if 'cmd' in curq:
                self.cmd = curq['cmd']
            print ("received: ", curq)
            if self.cmd == 'step':
                if 'value' in curq:
                    self.step = curq['value']
            elif self.cmd == 'min':
                if 'value' in curq:
                    self.minbright = int(float(curq['value'])*4095)
                    if self.minbright<0:
                        self.minbright = 0
                    if self.minbright > 4095:
                        self.minbright = 4095
            elif self.cmd == 'max':
                if 'value' in curq:
                    self.maxbright = int(float(curq['value'])*4095)
                    if self.maxbright<0:
                        self.maxbright = 0
                    if self.maxbright > 4095:
                        self.maxbright = 4095

            elif self.cmd == 'cycletime':
                if 'value' in curq:
                    self.cycle_time = float(curq['value'])
                    if self.cycle_time<self.mincycle_time:
                        self.cycle_time = self.mincycle_time
                    if self.cycle_time > self.maxcycle_time:
                        self.cycle_time = self.maxcycle_time

            elif self.cmd == 'steptime':
                if 'value' in curq:
                    self.step_time = float(curq['value'])
                    if self.step_time<self.minstep_time:
                        self.step_time = self.minstep_time
                    if self.step_time > self.maxstep_time:
                        self.step_time = self.maxstep_time

            elif self.cmd == 'faster':
                self.cycle_time -= self.cycle_time * 0.50
                if self.cycle_time < 1.0:
                    self.cycle_time = 1.0
            elif self.cmd == 'slower':
                self.cycle_time += self.cycle_time * 0.50
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
            self.update_status()
            return curq
        else: 
            return None

    def update_strands(self):
        for i in range(self.strands.num_strands):
            self.strands.pwm[i].set_pwm(self.strands.channel[i],
                                      0,self.strands.intensity[i])
                                      

    def run(self):
        self.run_lights =  True
        print('Running LEDs, press Ctrl-C to quit...')
        #x = 0
        #curside = 0
        start_time = time.time()
        start_step_time = start_time

        numstrands = len(self.strands.pwm)
        while not self.kill:
            curtime = time.time()
            cur_cycle_time = curtime- start_time # secs into this cycle
            if cur_cycle_time > self.cycle_time:
                start_time = time.time()
                start_step_time = start_time
                print('new cycle',cur_cycle_time)
                continue

            cur_step_time = curtime - start_step_time
            if cur_step_time < self.step_time:
                continue
##            print('new step',cur_step_time)
##            print('self.step_time: ',self.step_time)
            start_step_time = curtime

            #step is [0..1] and is time independent
            curstep = cur_cycle_time/ self.cycle_time
##            if cur_step_time >= self.step_time:
##                continue
##            if curstep > 1.0 :
##                starttime = curtime
##                continue
            if self.checkq():
                #something may have changed, recalc anything needed here
                
                continue
            
                
            if self.run_lights:

                for i in range(numstrands):
                    self.strands.intensity[i] = random.randint(self.minbright,self.maxbright)

                self.update_strands()

            else:
                time.sleep(self.step_time / 3.0 )

    def stop(self):
        self.run_lights = False

    def kill(self):
        self.kill = True
    

if __name__ == '__main__':



    lt = Lights()
    lt.start()

##    for step in [8,16,32,64,128,256]:
###    for step in [64,128,256]:
##        if lt.kill:
##            break
##
##        print("step is ", step)
##        lt.q.put({"cmd":"step","value":step})
##        #lt.step = step
##        for t in range(30):
##            if lt.kill:
##                break
##            time.sleep(1)

    #lt.stop()
    #lt.q.put({'cmd':'stop'})

    lt.q.put({'cmd':'max','value':0.001})
    print("ctrl-c to exit")
    while not lt.kill:
        time.sleep(3)
        pass

    


        
