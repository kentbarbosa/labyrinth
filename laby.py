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
#8/15/2016: handle separate cycle times for each transform
#           brightness is base transform - would be color if rgb
#8/17/2016: added strands.csv config file so lights can be configured on the fly and saved
#   todo: need to set up status queue
#   todo: move light and transform config into separate config file
#   todo: move back into flask to see if performance issue
#   todo: separate cycle times for each transform


from __future__ import division
from __future__ import print_function
import collections
from threading import Thread
import multiprocessing as mp
import Queue
import time
from multiprocessing.managers import BaseManager
import math
import pprint
import json
import csv


try:
    import Adafruit_PCA9685
    have_PCA9685 = True
except ImportError:
    have_PCA9685 = False


import random
import numpy as np
import numpy.ma as ma


strand_fields = ['pwm',
                'channel',
                'x',
                'y',
                'rho',
                'theta',
                'intensity' ]

class Lights(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill = False
        self.run_lights = False
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
        for i2c_addr in [ 0x40, 0x41 ]:
            try:
                self.pwm.append(Adafruit_PCA9685.PCA9685(address=i2c_addr))
            except NameError:
                self.pwm.append( None )
            
        for p in self.pwm:
            if p:
                p.set_pwm_freq(100)

        

        self.strands_config = []
        try:
            self.read_strands('strands.csv')
        except:
            self.add_strand( [ 1,  3,  6,  5, 1, 0, 0 ] )
            self.add_strand( [ 1,  2,  5,  6, 1, 1, 0 ] )
            self.add_strand( [ 1,  1,  4,  5, 1, 2, 0 ] )
            self.add_strand( [ 1,  0,  5,  4, 1, 3, 0 ] )
            self.add_strand( [ 0, 15,  7,  5, 2, 0, 0 ] )
            self.add_strand( [ 0, 14,  5,  7, 2, 1, 0 ] )
            self.add_strand( [ 0, 13,  3,  5, 2, 2, 0 ] )
            self.add_strand( [ 0, 12,  5,  3, 2, 3, 0 ] )
            self.add_strand( [ 0, 11,  8,  5, 3, 0, 0 ] )
            self.add_strand( [ 0, 10,  5,  8, 3, 1, 0 ] )
            self.add_strand( [ 0,  9,  2,  5, 3, 2, 0 ] )
            self.add_strand( [ 0,  8,  5,  2, 3, 3, 0 ] )
            self.add_strand( [ 0,  7,  9,  5, 4, 0, 0 ] )
            self.add_strand( [ 0,  6,  5,  9, 4, 1, 0 ] )
            self.add_strand( [ 0,  5,  1,  5, 4, 2, 0 ] )
            self.add_strand( [ 0,  4,  5,  1, 4, 3, 0 ] )
            self.add_strand( [ 0,  3, 10,  5, 5, 0, 0 ] )
            self.add_strand( [ 0,  2,  5, 10, 5, 1, 0 ] )
            self.add_strand( [ 0,  1,  0,  5, 5, 2, 0 ] )
            self.add_strand( [ 0,  0,  5,  0, 5, 3, 0 ] )

        self.write_strands('strands_backup.csv')

        self.update_strandinfo()

        self.transforms = collections.OrderedDict()
        self.transforms['brightness']= {'name':'brightness',
                                'active':True,
                                'value':1.0
                                }
        self.transforms['randomize']= {'name':'randomize',
                                'active':False,
                                'value':0.0
                                }
        self.transforms['rotate']= {'name':'rotate',
                                    'active':False,
                                    'value':0.0
                                    }
        self.transforms['xbounce']= {'name':'xbounce',
                                    'active':False,
                                    'value':0.0
                                    }
        self.transforms['ybounce']= {'name':'ybounce',
                                    'active':False,
                                    'value':0.0
                                    }
        for k,v in self.transforms.items():
            print('transform:',k)
            print(v)


        
        class QueueManager(BaseManager):pass
        QueueManager.register('get_queue')
        self.qmgr = QueueManager(address=('127.0.0.1',50001),authkey=b'labyrinth')
        self.qmgr.connect()
        self.q = self.qmgr.get_queue()

    def add_strand(self,data):
        self.strands_config.append(dict(zip(strand_fields,data)))
##        self.strands_config.append( {'pwm':pwm,
##                              'channel':channel,
##                              'x':x,
##                              'y':y,
##                              'rho':rho,
##                              'theta':theta,
##                              'intensity':intensity,
##                              })

    def read_strands(self,filename):
        self.strands_config = []
        with open(filename, 'rb') as csvfile:
            strands_reader = csv.reader(csvfile)
            for row in strands_reader:
##                print('row:')
##                print(row)
                if 6 <= len(row) <= 7 :
                    self.add_strand([int(i) for i in row]) 
##        print('read strands:')
##        print(self.strands_config)

    def write_strands(self,filename):
        with open(filename,'wb') as csvfile:
            strands_writer = csv.writer(csvfile)
            for s in self.strands_config:
                strands_writer.writerow([s[p] for p in strand_fields])
        pass
        
    def update_strandinfo(self):
        """create numpy arrays for the strands.
            updates min and max values for all strand fields.
            only needs to be called after building the model with add_strand in __init__
        """
        params = ['x','y','rho','theta']
        infos =  {'min':np.min,
                  'max':np.max,
                  'count':lambda x:len(set(x))}

        self.strands = {}

        for f in ['pwm','channel']:
            self.strands[f] = [ s[f] for s in self.strands_config]

        for f in params:
            if f in self.strands_config[0]:
                self.strands[f] = np.array([ s[f] for s in self.strands_config],dtype=np.int16)

        for f in ['intensity','last_intensity']:
            self.strands[f] = np.zeros_like(self.strands['x'],dtype=np.int16)

        self.strandinfo = { param: { info : None for info in infos} for param in params }
        for p in params:
            for ik,iv in infos.items():
                self.strandinfo[p][ik] = iv(self.strands[p])

        print('self.strands:', self.strands)
        print('strandinfo:',self.strandinfo)
                            
            

    def update_status(self):
    ##        print('cycle_time: ',self.cycle_time)
    ##        print('step_time: ',self.step_time)
    ##        print('maxbright: ',self.maxbright)
    ##        print('minbright: ',self.minbright)
        pass
        
        
    def checkq(self):
        if self.q and not self.q.empty():
            curq = self.q.get()
            if 'cmd' in curq:
                self.cmd = curq['cmd']
##            print ("received: ", curq)
            
            if self.cmd == 'min':
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
                    if p:
                        p.set_all_pwm(0,0)
                self.strands['intensity'] = np.zeros_like(self.strands['intensity'])
                self.run_lights = False
            elif self.cmd == 'transform':
##                print('got transform cmd, q: ',curq)
                if curq['name'] in self.transforms:
                    t_name = curq['name']
##                    print('t_name: {}'.format(t_name))

                    for k,v in curq.items():
##                        print("k: {}, v: {}".format(k,v))
                        if k == u'active':
                            if v in [u'True',u'true',u'On',u'on',u'1']:
                                self.transforms[t_name]['active'] = True
                            elif v in [u'False',u'false',u'Off',u'off',u'0']:
                                self.transforms[t_name]['active'] = False
                        elif k == u'value':
                            if v == 0.0:
                                self.transforms[t_name]['active'] = False
                            else:
                                self.transforms[t_name]['active'] = True
                            self.transforms[t_name]['value'] = v
                        else:
                            self.transforms[t_name][k] = v
                    #always have to have brightness active to get base intensity
                    self.transforms['brightness']['active'] = True
##                    print('updated transform {}: '.format(t_name))
##                    for k,v in self.transforms[t_name].items():
##                        print('{} : {}'.format(k,v))
                else:
                    print('not in transforms')
            self.q.task_done()
            self.update_status()
            return curq
        else: 
            return None
         
    def update_strands(self):
        changed = self.strands['intensity'] != self.strands['last_intensity']
        self.strands['last_intensity'] = self.strands['intensity'].copy()
        for i,c in enumerate(changed):
            if c:
                try:
                    self.pwm[self.strands['pwm'][i]].set_pwm(int(self.strands['channel'][i]),
                                            0,
                                            int(self.strands['intensity'][i]))
                except:
                    print( 'Exception: No PWM: pwm {}:{}, channel {}: intensity {} {}'.format(
                        self.strands['pwm'][i],
                        self.pwm[self.strands['pwm'][i]],
                        self.strands['channel'][i],
                        self.strands['intensity'][i],
                        self.strands['intensity'][i].dtype))
                           
    def randomize(self,step):
        self.strands['intensity'] = np.int16(self.strands['intensity'] * np.random.random(self.strands['intensity'].shape))
##        self.strands['intensity'] = np.random.randint(self.minbright,self.maxbright+1,
##                                                    self.strands['intensity'].shape)

    def brightness(self,step):
        self.strands['intensity'].fill(self.maxbright*self.transforms['brightness']['value'])

##        self.strands['intensity'] = np.full(self.strands['intensity'].shape,
##                                            self.maxbright*self.transforms['brightness']['value'],
##                                            dtype=np.int16)

    def rotate(self,step):
        """step is [0..1]"""
        thetamin = self.strandinfo['theta']['min']
        thetamax = self.strandinfo['theta']['max']
        thetarange = thetamax-thetamin
        thetacount = self.strandinfo['theta']['count'] 
        a = np.abs(np.cos(np.abs(self.strands['theta']-step*thetacount)/thetacount*np.pi))
        self.strands['intensity'] = np.int16(self.strands['intensity'] * a)

    def xybounce(self,step,axis,bounce):
        """step is [0..1]"""
        min = self.strandinfo[axis]['min']
        max = self.strandinfo[axis]['max']
        count = self.strandinfo[axis]['count'] 
##        print('min,max,range',min,max,sep='  ')
        a = np.abs(np.cos(np.abs(self.strands[axis]-step*count)/count*np.pi))
        a[self.strands[axis]==5] = 1.0 #ignores center strands
        self.strands['intensity'] = np.int16(self.strands['intensity'] * a)
##        print('strands: x, intensity: ',self.strands[axis],['intensity'])

    def xbounce(self,step,bounce=True):
        self.xybounce(step,'x',bounce)

    def ybounce(self,step,bounce=True):
        self.xybounce(step,'y',bounce)
        
    def transform(self,axis,step,bounce=True):
        """ axis : string 'x','y','rho','theta'
            step : [0,1] fraction of current cycle. determines where we are in cycle
            bounce : boolean :
            """
        pass

    def run(self):
        self.run_lights =  True
        #predetermine functions locally to try to speed up 
##        transform_func = { self.transforms[tname]['name']: eval('self.'+self.transforms[tname]['name'])
##                                       for tname in self.transforms.keys() }
##        print('transform_func:')
##        print(transform_func)
        print('Running LEDs...')
        start_time = time.time()
        start_step_time = start_time

        while not self.kill:
            curtime = time.time()
            cur_cycle_time = curtime- start_time # secs into this cycle
            if cur_cycle_time > self.cycle_time:
                start_time = time.time()
                start_step_time = start_time
                continue

            cur_step_time = curtime - start_step_time
            if cur_step_time < self.step_time:
                continue
            start_step_time = curtime

            #step is [0..1] and is time independent
            curstep = cur_cycle_time/ self.cycle_time
            if self.checkq():
                #something may have changed, recalc anything needed here
                
                continue
            
                
            if self.run_lights:

                for transform in self.transforms.values():
                    if transform['active']:
##                        print('Active transform: ',transform['name'])
##                        transform['func'](curstep);
                        eval('self.'+transform['name'])(curstep);
                        #todo
                        #transform_func[transform['name']](curstep); 
                self.update_strands()

            else:
                #time.sleep(self.step_time / 3.0 )
                pass

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

##    lt.q.put({'cmd':'max','value':0.001})
    lt.q.put({'cmd':'transform','name':'brightness','value':0.001})
    print("ctrl-c to exit")
    while not lt.kill:
        time.sleep(3)
        pass

    


        
