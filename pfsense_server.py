#!/usr/local/bin/python3.7
# Middleware (pfSense)
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid, time
import json
import requests
from PfsenseFauxapi.PfsenseFauxapi import PfsenseFauxapi
import random
import sys
import os

app = Flask(__name__)
app.config['SECRET_KEY']='Password1!'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////root//test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.wsgi_app=ProxyFix(app.wsgi_app)
migrate = Migrate(app, db)

class Devices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer)
    internal_device = db.Column(db.String(20))
    key = db.Column(db.String(100))
    device = db.Column(db.String(100))
 
class Translations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pfsense_port = db.Column(db.Integer)
    external_ip = db.Column(db.String(20))
    internal_ip = db.Column(db.String(20))
    device = db.Column(db.String(20))
    device_port = db.Column(db.Integer)
    key = db.Column(db.String(100))
    time = db.Column(db.String(30))

@app.before_request
def before_request():
    T1 = Translations.query.all()
    for i in T1:
        if int(time.time()) > int(i.time)+150:
            try:
                apiobj = PfsenseFauxapi('127.0.0.1', 'PFFATesting011', 'Password11Password11Password11Password11')
                config = apiobj.config_get() 
                for j in config['filter']['rule']:
                    if j['descr'] == i.device:
                        config['filter']['rule'].remove(j)
                for j in config['nat']['rule']:
                    if j['descr'] == i.device:
                        config['nat']['rule'].remove(j)
                apiobj.config_set(config)

                Translations.query.filter_by(device=i.device).delete()
                db.session.commit()
            except Exception as e:
                print(e)

@app.route("/")
def index():
    return {"Test":"Data"}

@app.route('/create/<device>', methods=['GET','POST'])
def createDevice(device):
    data = request.get_json(force=True)
    ip = request.remote_addr 
    d1 = Devices(port=data['port'], internal_device=ip, key=data['key'], device=device)
    db.session.add(d1)
    db.session.commit()
    return {"Message":"Success"}

@app.route('/open/<device>', methods=['POST'])
def openPort(device):
    try:
        data = request.get_json(force=True)
        t1 = int(time.time())
        src_ip = request.remote_addr
        pfsense_port = str(random.randint(40000,50000))
        ports = [t.pfsense_port for t in Translations.query.all()]
        while (pfsense_port in ports):
            pfsense_port = str(random.randint(40000,50000))

        d1 = Devices.query.filter_by(device=device).first_or_404()
        internal_port = d1.port
        src_interface = 'opt1'
        uid = uuid.uuid1()
        apiobj = PfsenseFauxapi('127.0.0.1', 'PFFATesting011', 'Password11Password11Password11Password11')
        config = apiobj.config_get()
        firewall_rule = {'associated-rule-id': '',
                          'created': {'time': str(t1),
                                      'username': 'NAT Port Forward'},
                          'descr': str(device),
                          'destination': {'address': str(d1.internal_device), 'port': str(internal_port)},
                          'interface': src_interface,
                          'ipprotocol': 'inet',
                          'protocol': 'tcp',
                          'source': {'address': src_ip},
                          'tracker': str(t1)}

        #nat_rule = {'associated-rule-id': '',
        nat_rule = {
                           'created': {'time': str(t1),
                                       'username': 'admin@192.168.1.10 (Local Database)'},
                           'descr': str(device),
                           'destination': {'network': 'opt1ip', 'port': pfsense_port},
                           'interface': src_interface,
                           'ipprotocol': 'inet',
                           'local-port': str(internal_port),
                           'protocol': 'tcp',
                           'source': {'any': ''},
                           'target': str(d1.internal_device),
                           'updated': {'time': str(t1),
                                       'username': 'admin@192.168.1.10 (Local Database)'}}

        config['filter']['rule'].append(firewall_rule)
        if 'rule' not in config['nat']:
            config['nat']['rule'] = [] 
        config['nat']['rule'].append(nat_rule)
        apiobj.config_set(config)
        ret1 = os.system('/etc/rc.filter_configure_sync')
        dport = Devices.query.filter_by(device=device).first_or_404().port
        t2 = Translations(pfsense_port=int(pfsense_port), external_ip=src_ip, internal_ip=d1.internal_device,device=device, device_port=dport, key=data['key'], time=t1)
        db.session.add(t2)
        db.session.commit()
    except Exception as e:
        return json.dumps({"Exit":str(e)})
    return json.dumps({"Port":int(pfsense_port), "Time":str(t1)})

@app.route('/delete/<device>/<time>', methods=['GET'])
def deleteTranslation(device, time):
    Translations.query.filter_by(device=device, time=time).delete()
    db.session.commit()
    apiobj = PfsenseFauxapi('127.0.0.1', 'PFFATesting011', 'Password11Password11Password11Password11', debug=True)
    config = apiobj.config_get()
    frules = config['filter']['rule']
    for j in frules:
        if j['descr'] == device and j['tracker'] == time:
            frules.remove(j)
    nrules = config['nat']['rule']
    for j in nrules:
        if j['descr'] == device and j['created']['time'] == time:
            nrules.remove(j)
    config['nat']['rule'] = nrules
    config['filter']['rule'] = frules
    apiobj.config_set(config)
    os.system('/etc/rc.filter_configure_sync')

    return {"Delete":"Success"}
    
if __name__ == '__main__':
    app.run()
