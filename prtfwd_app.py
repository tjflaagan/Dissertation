#!/usr/bin/python3
# Internal Server (Port Forward)
from flask import Flask, request
import requests
requests.packages.urllib3.disable_warnings()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return {"message":"Success Index"}

@app.route('/receive', methods=['GET', 'POST'])
def receiveTraffic():
    print(request.get_json(force=True))
    return {"message":"Success Recv"}

if __name__ == '__main__':
    app.run()
