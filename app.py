from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    x = {'Demands': [1,2,3,4,5,6,7,8,9]}
    return x
