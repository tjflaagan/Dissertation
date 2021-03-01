#!/bin/python
# External key generation
from flask import Flask, request
import requests
import json, os, time, uuid, sys

app = Flask(__name__)


@app.route('/generate', methods=['GET'])
def generateKey():
    print("Generate")
    # Hardcoding key for now, genera
    return json.dumps('{"key":"Password1!"}')


if __name__ == '__main__':
    app.run()
