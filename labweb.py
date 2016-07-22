from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from flask import Flask, render_template
app = Flask(__name__)


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


@app.route("/")
@app.route("/home")
def labyhome():
    templateData = get_status()
    templateData['title'] = 'The Labyrinth'
    return( render_template('home.html',**templateData))

@app.route("/stop")
def stoplights():
    cmdq.put({'cmd':'stop'})
    templateData = {
        'title':'The Labyrinth',
        }
    return( render_template('home.html',**templateData))

@app.route("/off")
def offlights():
    cmdq.put({'cmd':'off'})
    templateData = {
        'title':'The Labyrinth',
        }
    return( render_template('home.html',**templateData))

@app.route("/start")
def startlights():
    cmdq.put({'cmd':'start'})

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
