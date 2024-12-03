from flask import Flask, jsonify, request
import requests
import sqlite3
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


app.run(debug=True)
