# Imports
from flask import Flask
import os


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

# Import models and routes
from models import db
from routes import *

# Run the app
if __name__ == '__main__':
    app.run(debug = True)