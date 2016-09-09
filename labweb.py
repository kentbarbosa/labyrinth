from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from flask import Flask, render_template, redirect, request, jsonify
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
import atexit

app = Flask(__name__)
Mobility(app)

app.config.from_object('config')

#from .import views

sliders = { 'brightness':20}

cmdq = Queue()

import laby
global lt
lt = laby.Lights(cmdq)
lt.start()

cmdq.put({'cmd':'transform','name':'brightness','value':0.001})

def kill_lights():
    if lt:
        lt.kill()

atexit.register(kill_lights)



def get_status():
    status = {
        'alive': 'need to implementunknown',
        'step':'need to implement',
        'status':'need to implement',

        }
    return status

def home_page(template):
    templateData = get_status()
    templateData['title'] = 'Lighting Control'
    return( render_template(template,**templateData))

def redirect_home():
    return redirect("/home")

@app.route("/")
@mobile_template("m.html")
def index(template="home.html"):
    return( home_page(template))

@app.route("/home")
def labyhome():
    return( home_page("home.html"))

@app.route("/m")
def labymobile():
    templateData = get_status()
    return (render_template('m.html',**templateData))

@app.route("/params", methods=['GET','POST'])
def lightparams():
    form = LightParamsForm()
    return render_template('lightparams.html',
                           title='Light Parameters',
                           form=form)

@app.route("/stop")
def stoplights():
    cmdq.put({'cmd':'stop'})
    return( redirect_home())
@app.route("/kill")
def killlights():
    cmdq.put({'cmd':'kill'})
    return( redirect_home())

@app.route("/off")
def offlights():
    cmdq.put({'cmd':'off'})
    return( redirect_home())

@app.route("/start")
def startlights():
    cmdq.put({'cmd':'start'})
    return( redirect_home())

@app.route("/status")
def status():
    return( redirect_home())

@app.route("/faster")
def faster():
    cmdq.put({'cmd':'faster'})
    return(redirect_home())

@app.route("/slower")
def slower():
    cmdq.put({'cmd':'slower'})
    return(redirect_home())

@app.route("/cycletime/<cycle_time>")
def set_cycle_time(cycle_time):
    cmdq.put({'cmd':'cycletime',
              'value':cycle_time})
    return(redirect_home())

@app.route("/steptime/<step_time>")
def set_step_time(step_time):
    cmdq.put({'cmd':'steptime',
              'value':step_time})
    return(redirect_home())

@app.route("/max/<maxvalue>")
def set_maxbright(maxvalue):
    cmdq.put({'cmd':'max',
              'value':maxvalue})
    return(redirect_home())

@app.route("/transform")
def transform():
    cmd = {'cmd':'transform'}
    for k,v in request.args.items():
        cmd[k] = v.decode('utf-8')
    print('transform message:',cmd)
    cmdq.put(cmd)
    return(redirect_home())

@app.route("/_sliderchanged")
def sliderchanged():
    print('got slider change')
    print(request.args)
    slidername = request.args.get('name',None,type=str)
    sliderval = request.args.get('value',0,type=float)
    if slidername :
        sliders[slidername] = sliderval
    #send update to cmdmanager
    cmd = {'cmd':'transform',
           'name' : slidername,
           'value' : sliderval }
    print('transform message:',cmd)
    cmdq.put(cmd)
    return jsonify(name=slidername,val=sliderval)
              
@app.route("/_isactivechanged")
def isactivechanged():
    tname = request.args.get('name',None,type=str)
    isactive = request.args.get('active',None,type=str)
    cmd = {'cmd': 'transform',
           'name':tname,
           'active':isactive }
    cmdq.put(cmd)
    return jsonify({}) #todo

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
