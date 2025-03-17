from flask import Flask

app = Flask(__name__)
results = {}
predictionInput = None
predInputFormatted = None

#hier zu prüfmerkmal text voll ändern
#allCols = ['Prüfmerkmal_Text', 'Fertigungshilfsmittel', 'Sollwert', 'Merkmalsgewichtung', 'Maßeinheit', 'Oberer_Grenzwert', 'Unterer_Grenzwert', 'Nachkommastellen', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']
#inputCols = ['Prüfmerkmal_Text', 'Sollwert', 'Maßeinheit', 'Oberer_Grenzwert', 'Unterer_Grenzwert', 'Nachkommastellen', 'Vorgang', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']

#allCols = ['Prüfmerkmal_Text_Voll', 'Fertigungshilfsmittel', 'Sollwert', 'Merkmalsgewichtung', 'Maßeinheit', 'Oberer_Grenzwert', 'Unterer_Grenzwert', 'Stichprobenverfahren', 'Lenkungsmethode', 'Plangruppe', 'Verbindung', 'Vorgang', 'Arbeitsplatz', 'Beschreibung_Vorgang']
#inputCols = ['Prüfmerkmal_Text_Voll', 'Sollwert', 'Maßeinheit', 'Oberer_Grenzwert', 'Unterer_Grenzwert', 'Beschreibung_Vorgang', 'Plangruppe', 'Verbindung', 'Vorgang', 'Arbeitsplatz', 'Beschreibung_Vorgang']
#outputCols = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']

allCols = ['Produktmerkmal', 'Produktmerkmal_Text', 'Spezifikation', 'Unterer_Grenzwert', 'Oberer_Grenzwert', 'Prozesselement', 'Maschine', 'Prüfmittel', 'Stichprobenverfahren', 'Lenkungsmethode']
inputCols = ['Produktmerkmal', 'Produktmerkmal_Text', 'Spezifikation', 'Unterer_Grenzwert', 'Oberer_Grenzwert', 'Prozesselement', 'Maschine']
outputCols = ['Prüfmittel', 'Stichprobenverfahren', 'Lenkungsmethode']

from app import routes