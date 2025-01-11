from flask import Flask, render_template, request, url_for, redirect
import modelTrainer
import pandas as pd


app = Flask(__name__)

"""
def main():
    trainData = pd.read_excel('data//traindata.xlsx')
    predData = pd.read_excel('data//testdata.xlsx')
    modelType = 'rf'
    results = modelTrainer.createPrediction(trainData, predData, modelType)

    #display der ergebnisse zur probe
    print("______________________________")
    print("Full Results Matrix:")
    for outputvar in results: #results sind eine 2D Matrix: Jede Zeile ist eine Output-Variable und hat 4 Spalten.
      print(outputvar[0]) #Spalte 1: Modell
      print(outputvar[1]) #Spalte 2: Predictions in Zahlenform (Liste)
      print(outputvar[2]) #Spalte 3: Model Accuracy (Float) (Accuracy ist nur bei Training relevant, nicht bei neuen Predictions)
      print(outputvar[3]) #Spalte 4: Predictions in ursprünglicher Form (Das sind die Ergebnisse) (Liste)
      print("-------------")
    print("______________________________")
    return
"""

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/html')
def html():
    return render_template('index.html')

'''
@app.route('/auswertungen')
def auswertungen():
    return render_template('auswertungen.html')
'''


@app.route('/auswertungen', methods=['GET', 'POST'])
def index_func():
    #DAS IST FALSCH; NUR ZUM TESTEN OB ALLES FUNKTIONIERT, bis print(results)
    """
    trainData = pd.read_excel('data//traindata.xlsx')
    predData = pd.read_excel('data//testdata.xlsx')
    modelType = 'rf'
    results = modelTrainer.createPrediction(trainData, predData, modelType)
    print(results)
    """
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else

        #input-datei wird hier irgendwie hochgeladen
        #createPrediction funktion wird mit dieser input datei durchgeführt
        #am ende kommt die results matrix raus, damit kann man machen was man möchte
        
        """
        trainData = pd.read_excel('data//traindata.xlsx')
        predData = pd.read_excel('data//testdata.xlsx')
        modelType = 'rf'
        results = modelTrainer.createPrediction(trainData, predData, modelType)
        """
        return redirect(url_for('auswertungen'))
    # show the form, it wasn't submitted
    return render_template('auswertungen.html')

'''
@app.route('/monitoring', methods=['GET', 'POST'])
def index_func():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('monitoring'))
    # show the form, it wasn't submitted
    return render_template('monitoring.html')
'''

if __name__ == '__main__':
  app.run(debug=True)