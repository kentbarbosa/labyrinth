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
import collections
from threading import Thread
import multiprocessing as mp
import Queue
import time
from multiprocessing.managers import BaseManager
import math

import Adafruit_PCA9685
import random


##class Strands():
##    def __init__(self):
##        self.pwm=[]
##        self.channel=[]
##        self.x=[]
##        self.y=[]
##        self.rho=[]
##        self.theta=[]
##        self.intensity=[]
##        num_strands = 0
##
##    def add_strand(self,pwm,channel,x,y,rho,theta,intensity=0):
##        self.pwm.append(pwm)
##        self.channel.append(channel)
##        self.x.append(x)
##        self.y.append(y)
##        self.rho.append(rho)
##        self.theta.append(theta)
##        self.intensity.append(intensity)
##        self.num_strands = len(self.pwm)
##
##    def get_strand(self,i):
##        return { 'pwm': self.pwm[i],
##                 'channel': self.channel[i],
##                 'x':self.x[i],
##                 'y': self.y[i],
##                 'rho': self.rho[i],
##                 'theta':self.theta[i],
##                 'intensity':self.intensity[i],
##                 }

strand_fields = ['pwm',
                'channel',
                'x',
                'y',
                'rho',
                'theta',
                'intensity',
                'last_intensity' ]

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
            p.set_pwm_freq(100)

        

        def add_strand(pwm,channel,x,y,rho,theta,intensity=0):
            self.strands.append( {'pwm':pwm,
                                  'channel':channel,
                                  'x':x,
                                  'y':y,
                                  'rho':rho,
                                  'theta':theta,
                                  'intensity':intensity,
                                  'last_intensity':0, 
                                  })
        self.strands = []
        add_strand( self.pwm[1], 3, 6, 5, 1, 0, 0 )
        add_strand( self.pwm[1], 2, 5, 6, 1, 1, 0 )
        add_strand( self.pwm[1], 1, 5, 6, 1, 2, 0 )
        add_strand( self.pwm[1], 0, 5, 6, 1, 3, 0 )
        add_strand( self.pwm[0], 15, 5, 6, 2, 0, 0 )
        add_strand( self.pwm[0], 14, 5, 6, 2, 1, 0 )
        add_strand( self.pwm[0], 13, 5, 6, 2, 2, 0 )
        add_strand( self.pwm[0], 12, 5, 6, 2, 3, 0 )
        add_strand( self.pwm[0], 11, 5, 6, 3, 0, 0 )
        add_strand( self.pwm[0], 10, 5, 6, 3, 1, 0 )
        add_strand( self.pwm[0], 9, 5, 6, 3, 2, 0 )
        add_strand( self.pwm[0], 8, 5, 6, 3, 3, 0 )
        add_strand( self.pwm[0], 7, 5, 6, 4, 0, 0 )
        add_strand( self.pwm[0], 6, 5, 6, 4, 1, 0 )
        add_strand( self.pwm[0], 5, 5, 6, 4, 2, 0 )
        add_strand( self.pwm[0], 4, 5, 6, 4, 3, 0 )
        add_strand( self.pwm[0], 3, 5, 6, 5, 0, 0 )
        add_strand( self.pwm[0], 2, 5, 6, 5, 1, 0 )
        add_strand( self.pwm[0], 1, 5, 6, 5, 2, 0 )
        add_strand( self.pwm[0], 0, 5, 6, 5, 3, 0 )

        self.update_strandinfo()

        self.transforms = collections.OrderedDict()
        self.transforms['solid']= {'name':'solid',
                                'func':self.solid,
                                'active':True,
                                }
        self.transforms['randomize']= {'name':'randomize',
                                'func':self.randomize,
                                'active':False,
                                }
        self.transforms['rotate']= {'name':'rotate',
                                    'func':self.rotate,
                                    'active':True,
                                    }
        for k,v in self.transforms.items():
            print('transform:',k)
            print(v)


        
        class QueueManager(BaseManager):pass
        QueueManager.register('get_queue')
        self.qmgr = QueueManager(address=('127.0.0.1',50001),authkey=b'labyrinth')
        self.qmgr.connect()
        self.q = self.qmgr.get_queue()

    def update_strandinfo(self):
        """updates min and max values for all strand fields.
            only needs to be called after building the model with add_strand in __init__
        """
        params = ['x','y','rho','theta']
        infos =  ['min','max']
        self.strandinfo = { param: { info : None for info in infos} for param in params }
##        print('self.strands:',self.strands)
##        print('self.strandinfo:',self.strandinfo)
        for s in self.strands:
            for p in params:
                for i in infos:
                    if self.strandinfo[p][i] is None:
                        self.strandinfo[p][i] = s[p]
                    else:
##                        print('s[p],p,i,self.strandinfo[p][i]: ',s[p],p,i,self.strandinfo[p][i],sep=' ')
                        if i is 'min' and s[p] < self.strandinfo[p]['min']:
                            self.strandinfo[p]['min'] = s[p]
                        if i is 'max' and s[p] > self.strandinfo[p]['max']:
                            self.strandinfo[p]['max'] = s[p]

##        print('strandinfo:',self.strandinfo)
                            
            

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
            elif self.cmd == 'transform':
##                self.cmd_transform(curq)
                print('got transform cmd, q: ',curq)
                if curq['name'] in self.transforms:
                    t_name = curq['name']
##                    print('found itin transforms:',t_name)
##                    print('before update')
##                    print(self.transforms)
##                    for k,v in self.transforms[t_name].items():
##                        print('transkey',k)
##                        print('transval',v)
                        
                    for k,v in curq.items():
##                        print('curq key:',k)
##                        print('curq value:',v)
                        if k in self.transforms[t_name]:
##                            print('found in transforms')
                            if k == u'active':
##                                print('found active key')
                                if v in [u'True',u'true',u'On',u'on',u'1']:
                                    self.transforms[t_name]['active'] = True
                                elif v in [u'False',u'false',u'Off',u'off',u'0']:
                                    self.transforms[t_name]['active'] = False
                            else:
                                self.transforms[t_name][k] = v

##                    print('after update')
##                    print(self.transforms)
##                    for k,v in self.transforms[t_name].items():
##                        print('transkey',k)
##                        print('transval',v)
                else:
                    print('not in transforms')
            self.q.task_done()
            self.update_status()
            return curq
        else: 
            return None

##    def cmd_transform(self,curq):
##        """ update transforms based on commands in curq,
##            a dict provided by user
##        """
##        print('curq:',curq)
##        if 'name' in curq:
##            if curq['name'] in self.tranforms:
##                curtransform = curq['name']
##                del curq['name']
##                for k,v in curq.items():
##                    self.transforms[curtransform][k] = v
##                print('transform ',curtransform)
##                print(self.transforms[curtransform])
            
    def update_strands(self):
        for strand in self.strands:
            if strand['intensity'] != strand['last_intensity']:
                strand['pwm'].set_pwm(strand['channel'],0,strand['intensity'])
            strand['last_intensity'] = strand['intensity']           

    def randomize(self,step):
        for strand in self.strands:
            strand['intensity'] = random.randint(self.minbright,self.maxbright)

    def solid(self,step):
        for strand in self.strands:
            strand['intensity'] = self.maxbright

    def rotate(self,step):
        """step is 0..1"""
        thetamin = self.strandinfo['theta']['min']
        thetamax = self.strandinfo['theta']['max']
        thetarange = thetamax-thetamin
        thetacount = 4
##        print('min,max,range',thetamin,thetamax,thetarange,sep='  ')
        for strand in self.strands:
            a = abs(math.cos(abs(strand['theta']-step*thetacount)/thetacount*math.pi))
##            a = abs(math.sin((((strand['theta']-thetamin)/thetarange)+step)*math.pi))
            strand['intensity'] = int(strand['intensity'] * a)
##            print('strands: theta, intensity: ',strand['theta'],strand['intensity'])
        pass
        

    def run(self):
        self.run_lights =  True
        print('Running LEDs, press Ctrl-C to quit...')
        #x = 0
        #curside = 0
        start_time = time.time()
        start_step_time = start_time

        while not self.kill:
            curtime = time.time()
            cur_cycle_time = curtime- start_time # secs into this cycle
            if cur_cycle_time > self.cycle_time:
                start_time = time.time()
                start_step_time = start_time
##                print('new cycle',cur_cycle_time)
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

                for transform in self.transforms.values():
                    if transform['active']:
##                        print('Active transform: ',transform['name'])
                        transform['func'](curstep);
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

    


        
