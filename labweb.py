from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from flask import Flask, render_template, redirect, request, jsonify
app = Flask(__name__)

app.config.from_object('config')

#from .import views

from forms import LightParamsForm

sliders = { 'brightness':20}


class QueueManager(BaseManager):pass
QueueManager.register('get_queue')
qmgr = QueueManager(address=('127.0.0.1',50001),authkey=b'labyrinth')
qmgr.connect()
cmdq = qmgr.get_queue()


def get_status():
    status = {
        'alive': 'need to implementunknown',
        'step':'need to implement',
        'status':'need to implement',

        }
    return status

def home_page():
    templateData = get_status()
    templateData['title'] = 'Lighting Control'
    return( render_template('home.html',**templateData))

def redirect_home():
    return redirect("/home")

@app.route("/")
@app.route("/home")
def labyhome():
    return( home_page())

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
    slidername = request.args.get('id',None,type=str)
    sliderval = request.args.get('val',0,type=float)
    if slidername :
        sliders[slidername] = sliderval
    #send update to cmdmanager
    cmdq.put({'cmd':'max',
              'value':sliderval})
    return jsonify(name=slidername,val=sliderval)
              

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
