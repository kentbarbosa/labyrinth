from flask import Flask, render_template
app = Flask(__name__)

import laby
lt = laby.lightThread()
lt.start()

@app.route("/")
def labyhome():
    templateData = {
        'title':'The Labyrinth',
        'status':''
        }
    return( render_template('home.html',**templateData))

@app.route("/stop")
def stoplights():
    if lt.is_alive():
        lt.stop_lights()
    templateData = {
        'title':'The Labyrinth',
        'status':'Lights stopped'
        }
    return( render_template('home.html',**templateData))

@app.route("/start")
def startlights():
    if not lt.is_alive():
        lt.run()
    templateData = {
        'title':'The Labyrinth',
        'status':'Lights started'
        }
    return( render_template('home.html',**templateData))

@app.route("/status")
def status():
    #show light status
    templateData = {
        'title':'Status',
        'alive': 'True' if lt.is_alive() else 'False',
        'step':lt.step,
        }
    return( render_template('status.html',**templateData))





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
