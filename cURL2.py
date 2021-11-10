from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient

# global veriables
app = Flask(__name__)
LED_auth = HTTPBasicAuth()
Canvas_auth = HTTPBasicAuth()
client = MongoClient('localhost', 27017)
db = client["ECE4564_Assignment_3"]
collection = db["service_auth"]

# Username and password authentication block (LED route)
@LED_auth.verify_password
def verify_password(username, password):
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

# Username and password authentication block (Canvas Route)
@Canvas_auth.verify_password
def verify_password(username, password):
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
@LED_auth.error_handler
def auth_error(status):
    return "Access Denied ", status

@Canvas_auth.error_handler
def auth_error(status):
    return "Access Denied ", status

@app.route('/LED')
@LED_auth.login_required
def LED():
    command = request.args.get('command')
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]
    return status

@app.route('/Canvas')
@Canvas_auth.login_required
def canvas_API():
    # grab filename
    filename = request.args.get('file')
    # turn into a Python HTTP Request
    return filename


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)