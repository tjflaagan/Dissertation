#!/usr/bin/python3
# External Server
import requests
import json
requests.packages.urllib3.disable_warnings()

def sendInformation(device, m, port):
    r = requests.post('https://10.0.0.1:'+str(port)+'/receive', data=json.dumps({'message':m}), verify=False)
    #print(r.text)

def main():
    d1 = "UbuntuIoT"
    port = "51000"
    sendInformation(d1, "UpdateInfo", port)

if __name__ == '__main__':
    main()
