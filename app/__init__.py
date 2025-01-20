from flask import Flask

app = Flask(__name__)
results = None

from app import routes