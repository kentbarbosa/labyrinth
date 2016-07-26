from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from flask import Flask, render_template
app = Flask(__name__)

app.config.from_object('config')

#from .import views

from forms import LightParamsForm



class QueueManager(BaseManager):pass
QueueManager.register('get_queue')
qmgr = QueueManager(address=('127.0.0.1',50001),authkey='labyrinth')
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
    return( home_page())
@app.route("/kill")
def killlights():
    cmdq.put({'cmd':'kill'})
    return( home_page())

@app.route("/off")
def offlights():
    cmdq.put({'cmd':'off'})
    return( home_page())

@app.route("/start")
def startlights():
    cmdq.put({'cmd':'start'})
    return( home_page())

@app.route("/status")
def status():
    return( home_page())

@app.route("/faster")
def faster():
    cmdq.put({'cmd':'faster'})
    return(home_page())

@app.route("/slower")
def slower():
    cmdq.put({'cmd':'slower'})
    return(home_page())

@app.route("/cycletime/<cycle_time>")
def set_cycle_time(cycle_time):
    cmdq.put({'cmd':'cycletime',
              'value':cycle_time})
    return(home_page())

@app.route("/max/<maxvalue>")
def set_maxbright(maxvalue):
    cmdq.put({'cmd':'max',
              'value':maxvalue})
    return(home_page())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
