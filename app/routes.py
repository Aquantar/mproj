from app import app, results
from flask import Flask, render_template, request, url_for, redirect
from app.functions import *
from io import BytesIO

optionen = ["Option 1", "Option 2", "Option 3", "Option 4"]
predictionDummy = {'Fertigungshilfsmittel': ['MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'FORM- UND LAGEMESSGERÄT', 'MESSUHR', 'MESSUHR', 'Konturenmessgerät', 'FORM- UND LAGEMESSGERÄT', 'Konturenmessgerät', 'Rauhigkeitsmessgerät', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR'],
                   'Stichprobenverfahren': ['1/1', '2/30', '2/30', '1/1', '1/1', '2/30', '2/30', '2/30', '2/30', '1/222', '1/1', '1/444', '2/30', '1/1', '1/444', '1/444', '1/444', '1/222', '1/120', '2/30', '2/30', '1/120', '1/120', '2/30', '2/30', '2/30', '2/30', '1/222', '1/1'],
                   'Lenkungsmethode': [0.0, 0.0, 0.0, 33.0, 33.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 33.0, 0.0, 0.0, 0.0, 20.0, 20.0, 20.0, 33.0, 33.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],
                   'Merkmalsgewichtung': [0, 0, 0, 'HM', 'HM', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'HM', 'HM', 0, 0, 0, 0, 0, 0]
                  }

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def html():
    global results
    if request.method == 'POST':
        print("success. starting prediction")
        file = request.files['input']
        
        trainData = pd.read_excel('data//traindata.xlsx')
        predData = pd.read_excel(file)
        modelType = 'rf'
        #results = createPrediction(trainData, predData, modelType)         IST AUSKOMMENTIERT WEIL ES AKTUELL ZU LANGE DAUERT
        results = predictionDummy                                           #FÜRS ERSTE EINFACH DIESE RESULTS BENUTZEN, SIND DIE DUMMY WERTE VON OBEN

        return redirect(url_for('index_func'))
    return render_template('index.html')

@app.route('/auswertungen', methods=['GET', 'POST'])
def index_func():
    global results
    if request.method == 'POST':
        #results = request.form.get("meteodrop")
        outputForm = pd.read_excel('data//testdata_control.xlsx')
        outputForm = results[""]
    print(results)
    trainData = pd.read_excel('data//traindata.xlsx')
    unique_values = getUniqueValues(trainData)
    #prediction_dummy = predictionDummy
    print(getUniqueValues(trainData))

    return render_template('auswertungen.html', uniqueVals=unique_values, results=results)

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring_func():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('monitoring_func'))
    # show the form, it wasn't submitted
    return render_template('monitoring.html')