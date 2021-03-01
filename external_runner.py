#!/usr/bin/python3
# External Server
import requests
import json

requests.packages.urllib3.disable_warnings()
# Sends to middleware to start get port open
def openPort(device):
    r = requests.post('https://10.0.0.1:8080/open/%s' % device, data=json.dumps({'key':'Password1!'}), verify=False)
    return r

def sendInformation(device, m, port):
    r = requests.post('https://10.0.0.1:'+str(port)+'/receive', data=json.dumps({'message':m}), verify=False)
    # print(r.text)
def teardown(device, time):
    r = requests.get('https://10.0.0.1:8080/delete/%s/%s' % (device, time), verify=False)

def main():
    # print("Opening port")
    d1 = "UbuntuIoT"   
    r = openPort(d1)

    x = json.loads(r.text)
    print(x)
    sendInformation(d1, "UpdateInfo", x['Port'])

    # print("Tearing down translation...")
    teardown(d1,x['Time'])

if __name__ == '__main__':
    main()
