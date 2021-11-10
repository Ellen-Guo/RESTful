from flask import Flask
from flask import request
from flask_httpauth import HTTPBasicAuth
import pymongo
from pymongo import MongoClient
app = Flask(__name__)

auth = HTTPBasicAuth()

@app.verify_password
def verify_password(username, password):
    client = MongoClient('localhost', 27017)
    db = client["ECE4564_Assignment_3"]
    collection = db["service_auth"]
    name = user.get(username)
    secret = user.get(password)
    print(name, secret) #check and see if username and password is returned

@auth.error_handler
def auth_error(status):
    return "Access Denied: ", status

@app.route('/LED')
@auth.login_required
def LED():
    command = request.args.get('command')
    status = command[0:command.find('-')]
    color = command[command.find('-') + 1: command.find('-', command.find('-') + 1)]
    intensity = command[command.find('-', command.find('-') + 1) + 1:]

@app.route('/Canvas')
@auth.login_required
def canvas_API():
    # grab filename
    filename = request.args.get('file')
    # turn into a Python HTTP Request


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True)