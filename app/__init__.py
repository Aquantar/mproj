from flask import Flask

app = Flask(__name__)
results = {}
predictionInput = None
colsToPredict = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']

from app import routes