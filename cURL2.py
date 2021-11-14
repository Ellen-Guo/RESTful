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

#ip = 0
#port = 0
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
    def __init__(self):
        self.ip = get_ip()
        self.port = 8089

    def remove_service(self, zeroconf, type, name):
        print("service %s removed" % (name,))
        
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        
        ip_aton = None
        if info.name == "Testing._http._tcp.local.":
            for x in info.addresses:
                ip_aton = x
                break
            
            self.ip = socket.inet_ntoa(ip_aton)
            #ip = socket.inet_ntoa(ip_aton)
            self.port = info.port
            #port = info.port
                
        else:
            print("Address and name do not match")

    def show_data(self):
        return (self.ip, self.port)

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

# LED route
@app.route('/LED')
@auth.login_required
def LED():
    #ip = 0
    #port = 0
    
    command = request.args.get('command')
    # parsing of command from URL
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]
    
    #ip = get_ip()
    #port = 5000
    
    zeroconf = Zeroconf()
    listener = MyListener()
    address, portnum = listener.show_data()
    print(address, portnum)
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

    url = "http://%s:%s/LED?status=%s&color=%s&intensity=%s" % (str(address), str(portnum), status, color, intensity) 
    print(url)
    r = requests.get(url)
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