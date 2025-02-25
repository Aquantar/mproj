from app import app, results, predictionInput, inputCols, outputCols
from flask import Flask, render_template, request, url_for, redirect, make_response
from app.functions import *
from io import BytesIO
import xlsxwriter
from pickle import load, dump
import shutil
import os

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/prediction_results', methods=['GET', 'POST'])
def prediction_results():
    global results
    global predictionInput
    global outputCols
    if request.method == 'POST':
        import gzip
        predictionInput = request.files['input_prediction']
        conversionMap = load(open('models//model1//conversionMap.pkl', 'rb'))
        scaler = load(open('models//model1//scaler.pkl', 'rb'))
        for col in outputCols:
            model = load(gzip.open('models//model1//{}.pkl'.format(col), 'rb'))
            singleColResults = createPrediction(model, predictionInput, col, conversionMap, scaler)  
            results[col] = singleColResults
        print(results)           

        trainData = pd.read_excel('data//traindata_newcols.xlsx')  
        unique_values = getUniqueValues(trainData)
        print(unique_values)
        featureCount = len(results["Prüfmittel"])
        
        return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount= featureCount)
    return  #diese route sollte nie ohne einen POST trigger aufgerufen werden, deswegen hier einfach return atm

@app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
def prediction_results_confirmed():
    global results
    global predictionInput
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
        predictionOutput = predictionInput
        predictionOutput['Prüfmittel'] = list1
        predictionOutput['Stichprobenverfahren'] = list2
        predictionOutput['Lenkungsmethode'] = list3

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
        #file_training = request.files['input_training']
        #trainData = pd.read_excel(file_training)
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

        for col in outputCols:
            model, scaler, conversionMap = trainNewModel(trainData, col)                                                                                              
            dump(model, gzip.open('models//model1//{}.pkl'.format(col), 'wb'))
            dump(scaler, open('models//model1//scaler.pkl', 'wb'))
            dump(conversionMap, open('models//model1//conversionMap.pkl', 'wb'))

        trainData.to_excel("models//model1//currentTrainData.xlsx") 
        trainDataNew[0:0].to_excel("data//stashedTrainData.xlsx")

        return render_template('index.html')
    return  #diese route wird aktuell nie ohne einen POST trigger aufgerufen, deswegen hier einfach return atm

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    return render_template('monitoring.html')