from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient
import requests
import servicesKeys as key
import json

# global variables
app = Flask(__name__)
auth = HTTPBasicAuth()
get_header = requests.structures.CaseInsensitiveDict()
post_header = requests.structures.CaseInsensitiveDict()
course_id = 136283

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
    return "Access Denied Invalid Username and Password Provided. ", status

@app.route('/LED')
@auth.login_required
def LED():
    command = request.args.get('command')
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]
    return status
    # what does post to an LED do?

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
    print(filename)
    upload_para = {'file': open(filename, 'rb')}
    r_upload = requests.post(url=upload_url, files=upload_para)
    # format text returned
    upload_json = json.loads(r_upload.text)
    return_json = json.dumps(upload_json, indent=len(upload_json))
    return str(return_json)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)