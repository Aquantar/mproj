from flask import Flask

app = Flask(__name__)
results = {}
predInputFormatted = None
originalInputFile = None

allCols = ['Produktmerkmal', 'Produktmerkmal_Text', 'Spezifikation', 'Unterer_Grenzwert', 'Oberer_Grenzwert', 'Masseinheit', 'Prozesselement', 'Maschine', 'Prüfmittel', 'Stichprobenverfahren', 'Lenkungsmethode']
inputCols = ['Produktmerkmal', 'Produktmerkmal_Text', 'Spezifikation', 'Unterer_Grenzwert', 'Oberer_Grenzwert', 'Masseinheit', 'Prozesselement', 'Maschine']
outputCols = ['Prüfmittel', 'Stichprobenverfahren', 'Lenkungsmethode']

from app import routes