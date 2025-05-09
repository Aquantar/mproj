from app import app, results, predictionInput, inputCols, outputCols, predInputFormatted
from flask import Flask, render_template, request, url_for, redirect, make_response
from app.functions import *
from io import BytesIO
import xlsxwriter
from pickle import load, dump
import shutil
import os
import pandas as pd
import re
"""from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

auth = HTTPBasicAuth()
users = {
    "admin": generate_password_hash("meinpasswort", method='pbkdf2:sha256')
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

@app.route('/monitoring', methods=['GET', 'POST'])
@auth.login_required
def monitoring():
    return render_template('monitoring.html')"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/prediction_results', methods=['GET', 'POST'])
def prediction_results():
    global results
    global outputCols
    global predInputFormatted
    if request.method == 'POST':
        import gzip
        predictionInput = request.files['input_prediction']
        conversionMap = load(open('models//model1//conversionMap.pkl', 'rb'))   #load conversion map of current model
        scaler = load(open('models//model1//scaler.pkl', 'rb')) #load scaler of current model
        predInputFormatted = convertPredDataToDataframe(predictionInput) #take input file, convert into dataframe to be used for predictions
        probaDict = {}
        for col in outputCols:  #perform prediction for each desired predicted feature
            model = load(gzip.open('models//model1//{}.pkl'.format(col), 'rb')) #load current model
            singleColResults, probaTuple = createPrediction(model, predInputFormatted, col, conversionMap, scaler) #create predictions for current feature
            results[col] = singleColResults
            probaDict[col] = probaTuple
        #print(probaDict)
        for key, value in results.items():  #add output features to input
            predInputFormatted[key] = value

        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')  #open train data to extract all unique values
        unique_values = getUniqueValues(trainData)
        
        return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount=len(predInputFormatted.index), predictionInput=predInputFormatted.to_dict(orient='records'), probaDict=probaDict)
    return  #diese route sollte nie ohne einen POST trigger aufgerufen werden, deswegen hier einfach return atm

@app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
def prediction_results_confirmed():
    global results
    global predInputFormatted
    if request.method == 'POST':
        #replace predicted values with modified ones from results form
        choicesOutput = request.form
        list1 = []
        list2 = []
        list3 = []
        for key, value in choicesOutput.items(multi=True):
            valTrimmed = re.sub(r' \(\d+%\)', '', value)
            print(valTrimmed)
            if key == "Prüfmittel":
                list1.append(valTrimmed)
            if key == "Stichprobenverfahren":
                list2.append(valTrimmed)
            if key == "Lenkungsmethode":
                list3.append(valTrimmed)
        predictionOutput = predInputFormatted
        predictionOutput['Prüfmittel'] = list1
        predictionOutput['Stichprobenverfahren'] = list2
        predictionOutput['Lenkungsmethode'] = list3

        #update stashedTrainData with new rows
        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')
        trainData = trainData.astype(str)
        predictionOutput = predictionOutput.astype(str)
        newData = pd.merge(predictionOutput,trainData, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
        stashedData = pd.read_excel('models//stashedTrainData.xlsx')
        stashedData = stashedData.astype(str)
        stashedData = pd.concat([stashedData, newData]).drop_duplicates()
        stashedData = stashedData.replace(['nan'], [""]) 
        with pd.ExcelWriter("models//stashedTrainData.xlsx") as writer:
            stashedData.to_excel(writer, index=False)  
         
        #export results to excel and download
        sio = BytesIO()
        outputName = "output"
        writerImportsheet = pd.ExcelWriter("{}.xlsx".format(outputName), engine="xlsxwriter")
        predictionOutput.to_excel(writerImportsheet, sheet_name="Sheet1", index=False)
        workbook = xlsxwriter.Workbook(sio)
        sheet = workbook.add_worksheet(u'Sheet1')
        columns = list(predictionOutput.columns.values) 
        iter = 0
        for col in columns:
            sheet.write(0, iter, col)
            full_column = predictionOutput.iloc[:, iter]
            row = 0
            while row < len(full_column):
                try:
                    sheet.write(row+1, iter, full_column[row])
                    row = row + 1
                except:
                    row = row + 1
                    pass
            iter = iter + 1
        workbook.close()
        sio.seek(0)
        resp = make_response(sio.getvalue())
        resp.headers["Content-Disposition"] = "attachment; filename={}.xlsx".format(outputName)
        resp.headers['Content-Type'] = 'application/x-xlsx'
        return resp
    return #diese route sollte auch nie ohne POST aufgerufen werden können, aber vllt automatisch zurück zu index redirecten nachdem POST fertig ist?

@app.route('/model_training', methods=['GET', 'POST'])
def model_training():
    global outputCols
    if request.method == 'POST':
        import gzip

        dir1 = 'models//model1'
        dir2 = 'models//model2'
        dir3 = 'models//model3'

        for fileName in os.listdir(dir2):
            shutil.copy(os.path.join(dir2, fileName), dir3)

        for fileName in os.listdir(dir1):
            shutil.copy(os.path.join(dir1, fileName), dir2)

        #get both current train data and stashed rows, and combine them
        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')
        trainDataNew = pd.read_excel('models//stashedTrainData.xlsx')
        trainData = pd.concat([trainData, trainDataNew])
        trainData = trainData.dropna(how="all")

        #train new models, and create files
        accuracyList = []
        for col in outputCols:
            model, scaler, conversionMap, accuracy = trainNewModel(trainData, col)                                                                                              
            dump(model, gzip.open('models//model1//{}.pkl'.format(col), 'wb'))
            dump(scaler, open('models//model1//scaler.pkl', 'wb'))
            dump(conversionMap, open('models//model1//conversionMap.pkl', 'wb'))
            accuracyList.append(accuracy)

        #export train data
        trainData.to_excel("models//model1//currentTrainData.xlsx", index=False) 
        stashedTrainingDataOverride = pd.DataFrame(columns=list(trainData.columns.values))
        stashedTrainingDataOverride.to_excel("models//stashedTrainData.xlsx", index=False)

        #update and export model metrics
        modelMetrics = pd.read_excel('models//modelData.xlsx')
        modelID = len(modelMetrics)+1
        from datetime import datetime
        newrow = [modelID, datetime.today().strftime('%Y-%m-%d'), accuracyList[0], accuracyList[1], accuracyList[2]]
        modelMetrics.loc[len(modelMetrics)] = newrow
        modelMetrics.to_excel("models//modelData.xlsx", index=False)

        accuracyData = []
        accuracyData_1 = [float(i) for i in modelMetrics['accuracy_1'].tolist()]
        accuracyData_2 = [float(i) for i in modelMetrics['accuracy_2'].tolist()]
        accuracyData_3 = [float(i) for i in modelMetrics['accuracy_3'].tolist()]
        accuracyData.append(accuracyData_1)
        accuracyData.append(accuracyData_2)
        accuracyData.append(accuracyData_3)
        modelIDs = modelMetrics['modelID'].tolist()

        return render_template("monitoring.html", accuracyData=accuracyData, modelIDs=modelIDs)
    return  #diese route wird aktuell nie ohne einen POST trigger aufgerufen, deswegen hier einfach return atm

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    if request.method == 'POST':
        modelMetrics = pd.read_excel('models//modelData.xlsx')
        accuracyData = []
        accuracyData_1 = [float(i) for i in modelMetrics['accuracy_1'].tolist()]
        accuracyData_2 = [float(i) for i in modelMetrics['accuracy_2'].tolist()]
        accuracyData_3 = [float(i) for i in modelMetrics['accuracy_3'].tolist()]
        accuracyData.append(accuracyData_1)
        accuracyData.append(accuracyData_2)
        accuracyData.append(accuracyData_3)
        modelIDs = modelMetrics['modelID'].tolist()

        return render_template("monitoring.html", accuracyData=accuracyData, modelIDs=modelIDs)
    return render_template("monitoring.html", accuracyData=[])
    
@app.route('/stasheddata', methods=['GET', 'POST'])
def stasheddata():
    file_path = os.path.join("models", "stashedTrainData.xlsx")

    # Prüfen, ob Datei existiert
    if not os.path.exists(file_path):
        return render_template("stasheddata.html", data=None, error="Datei nicht gefunden")

    try:
        df = pd.read_excel(file_path, header=0, dtype=str)  # Alle Werte als Strings für Konsistenz
        
        if df.empty:
            return render_template("stasheddata.html", data=None, error="Die Datei ist leer")
        
        # NaN-Werte ersetzen
        df = df.fillna("--")

        # HTML-kompatible Tabelle generieren
        table_html = df.to_html(classes='table table-striped', index=False)
        return render_template("stasheddata.html", data=table_html, error=None)

    except Exception as e:
        return render_template("stasheddata.html", data=None, error=str(e))