from flask import Flask
import datetime
import json
app = Flask(__name__)
datetime = datetime.datetime.now()
@app.route("/")
def hello():
    x = {'Demands': [1,2,3,4,5,6,7,8,9]}
    return json.dumps(x)
