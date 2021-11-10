from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient
import requests
import serviceKeys

# global variables
app = Flask(__name__)
auth = HTTPBasicAuth()

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

@app.route('/LED')
@auth.login_required
def LED():
    command = request.args.get('command')
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]
    return status
    # what does post to an LED do?

@app.route('/Canvas', methods='GET')
@auth.login_required
def canvas_API():
    # grab filename
    filename = request.args.get('file')
    # is the full complete path to the file provided or just the filename?
    # get is retrieving the item and post and uploading an item to canvas?
    # is there a specific location the posted files should end up?
    # so we are not using the canvasapi library, just the python requests library...
    # turn into a Python HTTP Request
    r = requests.get(filename)
    return filename

@app.route('/Canvas', methods='POST')
@auth.login_required
def canvas_API():
    # grab filename
    filename = request.args.get('file')
    # turn into a Python HTTP Request
    r = requests.post(filename)
    return filename


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)