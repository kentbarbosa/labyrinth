from multiprocessing import Process, Queue
from flask import Flask, render_template
app = Flask(__name__)


cmdq = Queue()

import laby
lt = laby.lightThread(q=cmdq)
lt.start()

def get_status():
    status = {
        'alive': 'True' if lt.is_alive() else 'False',
        'step':lt.step,
        'status':'--status goes here--',

        }
    return status


@app.route("/")
def labyhome():
    templateData = get_status()
    templateData['title'] = 'The Labyrinth'
    return( render_template('home.html',**templateData))

@app.route("/stop")
def stoplights():
    #if lt.is_alive():
##    lt.stop()
    cmdq.put({'command':'stop'})
    templateData = {
        'title':'The Labyrinth',
        }
    return( render_template('home.html',**templateData))

@app.route("/start")
def startlights():
    if lt and not lt.is_alive():
        lt.run()
    cmdq.put({'command':'start')}

    templateData = {
        'title':'The Labyrinth',
        'status':'Lights started'
        }
    return( render_template('home.html',**templateData))

@app.route("/status")
def status():
    #show light status
    templateData = get_status()
    print "Status update"
    print templateData
    return( render_template('status.html',**get_status()))





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
