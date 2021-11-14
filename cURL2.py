from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient
from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
import socket
import requests


# global variables
app = Flask(__name__)
auth = HTTPBasicAuth()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def signal_handler(signal, frame):
    print("Interrupt called")
    zeroconf.unregister_service(info)
    zeroconf.close()
    sys.exit(0)
    
class MyListener(object):
    def remove_service(self, zeroconf, type, name):
        print("service %s removed" % (name,))
        
    def add_service(self, zeroconf, type, name):
        global ip, port
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        
        ip_aton = None
        if info.name == "Testing._http._tcp.local.":
            for x in info.addresses:
                ip_aton = x
                break
            
            ip = socket.inet_ntoa(ip_aton)
            port = info.port
            color = info.properties
            print('Inside: ', ip, port, color)
                
        else:
            print("Address and name do not match")

zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

# Username and password authentication block (LED route)
@auth.verify_password
def verify_password(username, password):
    client = MongoClient('localhost', 27017)
    db = client["ECE4564_Assignment_3"]
    collection = db["service_auth"]
    user_entry = {"username":str(username), "password":str(password)}
    doc = collection.find(user_entry) # locate query in database
    # validate and check cursor entry within the database for authentication
    if doc == None:
        doc.close() # delete and reallocate cursor resource
        return False
    else:
        for x in doc:
            user = x["username"]
            secret = x["password"]
            doc.close() # delete and reallocate cursor resource
            return (user == username) and (secret == password)

# Authentication Error Handler
@auth.error_handler
def auth_error(status):
    return "Access Denied ", status

# LED routes
@app.route('/LED', method=['POST'])
@auth.login_required
def post_LED():
    global ip, port
    command = request.args.get('command')
    # parsing of command from URL
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]
    
    print('Inside Flask: ', ip, port)
    url = "http://%s:%s/LED?status=%s&color=%s&intensity=%s" % (str(ip), str(port), status, color, intensity) 
    print(url)
    r = requests.post(url)
    return r.text

@app.route('/LED', method=['GET'])
@auth.login_required
def get_LED():
    global ip, port

    print('Inside Flask: ', ip, port)
    url = "http://%s:%s/LED" % (str(ip), str(port)) 
    print(url)
    r = requests.post(url)
    # might need to json the return
    return r.text
    

# Canvas route
@app.route('/Canvas')
@auth.login_required
def canvas_API():
    # grab filename
    filename = request.args.get('file')
    # turn into a Python HTTP Request
    return filename


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)