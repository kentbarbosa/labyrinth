                for i in range(0,4095,self.step):
##                    for w in self.walls:
##                        w.pwm.set_pwm(w.channel,4095-i)
##                    for p in self.pwm:
##                        p.set_all_pwm(0,4095-i)
##                        for c in range(16):
##                            p.set_pwm(c,0,4095-i)
                    
                    #self.pwm[0].set_pwm(0,0,4095-i)
    ##                pwm[1].set_pwm(0,0,4095-i)
                    #self.pwm[0].set_pwm(7,0,i)

    ##                for side in range(4,8):
    ##                    self.pwm[1].set_pwm(side,0,i)
                    #time.sleep(w)
                for i in range(4095,0,-self.step):
                    for p in self.pwm:
                        p.set_all_pwm(0,4095-i)
                        
##                        for c in range(16):
##                            p.set_pwm(c,0,4095-i)

                    #self.pwm[0].set_pwm(0,0,4095-i)
    ##                self.pwm[1].set_pwm(0,0,4095-i)
                    #self.pwm[0].set_pwm(7,0,i)
    ##                for side in range(4,8):
    ##                    self.pwm[1].set_pwm(side,0,i)
