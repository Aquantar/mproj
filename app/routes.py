from app import app, results, predictionInput, inputCols, outputCols, predInputFormatted
from flask import Flask, render_template, request, url_for, redirect, make_response
from app.functions import *
from io import BytesIO
import xlsxwriter
from pickle import load, dump
import shutil
import os
import pandas as pd

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
        conversionMap = load(open('models//model1//conversionMap.pkl', 'rb'))
        scaler = load(open('models//model1//scaler.pkl', 'rb'))
        predInputFormatted = convertPredDataToDataframe(predictionInput)
        for col in outputCols:
            model = load(gzip.open('models//model1//{}.pkl'.format(col), 'rb'))
            singleColResults = createPrediction(model, predictionInput, col, conversionMap, scaler)  
            results[col] = singleColResults
            predInputFormatted[col] = singleColResults
        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')  
        unique_values = getUniqueValues(trainData)
        featureCount = len(results["Prüfmittel"])
        
        return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount= featureCount, predictionInput=predInputFormatted.to_dict(orient='records'))
    return  #diese route sollte nie ohne einen POST trigger aufgerufen werden, deswegen hier einfach return atm

@app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
def prediction_results_confirmed():
    global results
    global predInputFormatted
    if request.method == 'POST':
        choicesOutput = request.form
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        for key, value in choicesOutput.items(multi=True):
            if key == "Prüfmittel":
                list1.append(value)
            if key == "Stichprobenverfahren":
                list2.append(value)
            if key == "Lenkungsmethode":
                list3.append(value)
        predictionOutput = predInputFormatted
        predictionOutput['Prüfmittel'] = list1
        predictionOutput['Stichprobenverfahren'] = list2
        predictionOutput['Lenkungsmethode'] = list3

        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')
        trainData = trainData.astype(str)
        print("TRAIND DATA")
        print(trainData)
        predictionOutput = predictionOutput.astype(str)
        print("PREDOUT")
        print(predictionOutput)
        newData = pd.merge(predictionOutput,trainData, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
        print("newDat")
        print(newData)
        stashedData = pd.read_excel('data//stashedTrainData.xlsx')
        stashedData = stashedData.astype(str)
        stashedData = pd.concat([stashedData, newData]).drop_duplicates()
        #stashedData.drop(stashedData.columns[0],axis=1,inplace=True)
        stashedData = stashedData.replace(['nan'], [""]) 
        with pd.ExcelWriter("data//stashedTrainData.xlsx") as writer:
            stashedData.to_excel(writer, index=False)  
         
        #export results to excel and download
        sio = BytesIO()
        outputName = "output"
        writerImportsheet = pd.ExcelWriter("{}.xlsx".format(outputName), engine="xlsxwriter")
        predictionOutput.to_excel(writerImportsheet, sheet_name="Sheet1", index=False)
        workbook = xlsxwriter.Workbook(sio)
        sheet = workbook.add_worksheet(u'Sheet1')
        #Header
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
        import pickle

        dir1 = 'models//model1'
        dir2 = 'models//model2'
        dir3 = 'models//model3'

        for fileName in os.listdir(dir2):
            shutil.copy(os.path.join(dir2, fileName), dir3)

        for fileName in os.listdir(dir1):
            shutil.copy(os.path.join(dir1, fileName), dir2)

        trainData = pd.read_excel('models//model1//currentTrainData.xlsx')
        trainDataNew = pd.read_excel('data//stashedTrainData.xlsx')
        trainData = pd.concat([trainData, trainDataNew])
        trainData = trainData.dropna(how="all")

        accuracyList = []
        for col in outputCols:
            model, scaler, conversionMap, accuracy = trainNewModel(trainData, col)                                                                                              
            dump(model, gzip.open('models//model1//{}.pkl'.format(col), 'wb'))
            dump(scaler, open('models//model1//scaler.pkl', 'wb'))
            dump(conversionMap, open('models//model1//conversionMap.pkl', 'wb'))
            accuracyList.append(accuracy)

        trainData.to_excel("models//model1//currentTrainData.xlsx", index=False) 
        stashedTrainingDataOverride = pd.DataFrame(columns=list(trainData.columns.values))
        stashedTrainingDataOverride.to_excel("data//stashedTrainData.xlsx", index=False)

        modelMetrics = pd.read_excel('models//modelData.xlsx')
        print(modelMetrics)
        modelID = len(modelMetrics)+1
        from datetime import datetime
        newrow = [modelID, datetime.today().strftime('%Y-%m-%d'), accuracyList[0], accuracyList[1], accuracyList[2]]
        print(newrow)
        modelMetrics.loc[len(modelMetrics)] = newrow
        modelMetrics.to_excel("models//modelData.xlsx", index=False)

        return render_template('index.html')
    return  #diese route wird aktuell nie ohne einen POST trigger aufgerufen, deswegen hier einfach return atm

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    return render_template("monitoring.html")
    
@app.route('/stasheddata', methods=['GET', 'POST'])
def stasheddata():
    file_path = os.path.join("data", "stashedTrainData.XLSX")

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