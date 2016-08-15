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


<script type="text/javascript"
  src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>

    <script type="text/javascript" src="static/jquery.min.js"></script>


        $.getJSON($SCRIPT_ROOT + '/_sliderchanged', {
            $(this).id : $(this).val()
            },
            function(data) {
                $("p." + data.name).text(data.val);
                }
            )
        }


    var submit_form = function(e) {
      $.getJSON($SCRIPT_ROOT + '/_sliderchanged', {
        a: $('input[name="a"]').val(),
        b: $('input[name="b"]').val()
      }, function(data) {
        $('#result').text(data.result);
        $('input[name=a]').focus().select();
      });
      return false;
    };


      <form>
      <input id="brightness" type="range" class="slider" value="0.1" min="0.0" max="1.0" step="0.01">
      </form>
    <p id="brightness" >_init_ brightness </p>
      <br>
