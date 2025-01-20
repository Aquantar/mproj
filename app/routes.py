from app import app, results
from flask import Flask, render_template, request, url_for, redirect
from app.functions import *
from io import BytesIO

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def html():
    global inputFile
    if request.method == 'POST':
        print("success. starting prediction")
        file = request.files['input']
        trainData = pd.read_excel(file)
        predData = pd.read_excel('data//testdata.xlsx')
        modelType = 'rf'
        results = createPrediction(trainData, predData, modelType)
        return redirect(url_for('index_func'))
    return render_template('index.html')

@app.route('/auswertungen', methods=['GET', 'POST'])
def index_func():
    print(results)

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