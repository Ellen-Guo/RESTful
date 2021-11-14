from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient
from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
import socket
import requests
import servicesKeys as key
import json


app = Flask(__name__)
auth = HTTPBasicAuth()
# canvas items
get_header = requests.structures.CaseInsensitiveDict()
post_header = requests.structures.CaseInsensitiveDict()
course_id = 136283
# global variables
global ip, port
ip = None
port = None

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
    return "Access Denied Invalid Username or Password. ", status

# LED routes
@app.route('/LED', methods=['POST'])
@auth.login_required
def post_LED():
    global ip, port
    command = request.args.get('command')
    if ip == None:
        output = 'Error: LED Pi Service Not Available'
    else:
        if command == 'off':
            status = command
            url = "http://%s:%s/LED?status=%s" % (str(ip), str(port), status) 
        else:
            # parsing of command from URL
            status = command[0:command.find('-')]
            color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
            intensity = command[command.find('-', command.find('-') + 1) + 1:]
            url = "http://%s:%s/LED?status=%s&color=%s&intensity=%s" % (str(ip), str(port), status, color, intensity) 
        r = requests.post(url)
        output = r.text
    return output

@app.route('/LED', methods=['GET'])
@auth.login_required
def get_LED():
    global ip, port
    if ip == None:
        output = 'Error: LED Pi Service Not Available'
    else:
        url = "http://%s:%s/LED" % (str(ip), str(port)) 
        r = requests.get(url)
        output = r.text
    return output

# Canvas routes
@app.route('/Canvas', methods=['GET'])
@auth.login_required
def canvas_API_get():
    canvas_get_url = 'https://vt.instructure.com/api/v1/courses/'+ str(course_id) +'/files/'
    # grab filename
    filename = request.args.get('file')
    get_header["Authorization"] = 'Bearer ' + str(key.canvas_tok)
    r = requests.get(canvas_get_url + '?search_term=' + str(filename), headers = get_header)
    file_id = r.text[r.text.find("id")+4:r.text.find(",")]
    # get file download link
    file_info = requests.get(canvas_get_url + str(file_id), headers=get_header)
    start_url = file_info.text.find("url")+6
    canvas_get_file = file_info.text[start_url:file_info.text.find(",", start_url, -1)-1]
    file_content = requests.get(canvas_get_file, headers=get_header, allow_redirects=True)
    open(str(filename), 'wb').write(file_content.content)
    # format header and return
    json_return = json.dumps(dict(file_content.headers), indent=7)
    return str(json_return)

@app.route('/Canvas', methods=['POST'])
@auth.login_required
def canvas_API_post():
    canvas_post_url = 'https://vt.instructure.com/api/v1/users/self/files'
    # grab filename
    filename = request.args.get('file')
    f_content = request.files['file'].read()
    open(str(filename), "wb").write(f_content)
    # turn into a Python HTTP Request
    post_header["Authorization"] = 'Bearer %s' % key.canvas_tok
    post_header["parent_folder_path"] = "/"
    post_header["name"]=filename
    r = requests.post(url=canvas_post_url, headers=post_header)
    # get upload url and parameters to make file post
    response = json.loads(r.text)
    upload_url = response["upload_url"]
    upload_para = {'file': open(filename, 'rb')}
    r_upload = requests.post(url=upload_url, files=upload_para)
    # format text returned
    upload_json = json.loads(r_upload.text)
    return_json = json.dumps(upload_json, indent=len(upload_json))
    return str(return_json)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)