from flask import Flask
import datetime
datetime = datetime.datetime.now()
app = Flask(__name__)

@app.route("/")
def hello():
    if datetime.minute%5 == 0:
        x = {'Demands': [1,2,3,4,5,6,7,8,9]}
        return x
    else:
        x = {'Time': [datetime.hour,':',datetime.minute]}
        return x
