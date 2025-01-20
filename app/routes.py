from app import app
from flask import Flask, render_template, request, url_for, redirect
from app.functions import *

@app.route('/')
@app.route('/index')
def html():
    return render_template('index.html')

@app.route('/auswertungen', methods=['GET', 'POST'])
def index_func():
    #DAS IST FALSCH; NUR ZUM TESTEN OB ALLES FUNKTIONIERT, bis print(results)
    
    trainData = pd.read_excel('data//traindata.xlsx')
    predData = pd.read_excel('data//testdata.xlsx')
    modelType = 'rf'
    results = createPrediction(trainData, predData, modelType)
    print(results)
    
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

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring_func():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('monitoring_func'))
    # show the form, it wasn't submitted
    return render_template('monitoring.html')