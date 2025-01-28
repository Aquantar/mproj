from app import app, results, predictionInput, colsToPredict
from flask import Flask, render_template, request, url_for, redirect, make_response
from app.functions import *
from io import BytesIO
import xlsxwriter

#use this for quick testing to not wait for real predictions (overwrite results variable with this)
predictionDummy = {'Fertigungshilfsmittel': ['MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'FORM- UND LAGEMESSGERÄT', 'MESSUHR', 'MESSUHR', 'Konturenmessgerät', 'FORM- UND LAGEMESSGERÄT', 'Konturenmessgerät', 'Rauhigkeitsmessgerät', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR', 'MESSUHR'],
                   'Stichprobenverfahren': ['1/1', '2/30', '2/30', '1/1', '1/1', '2/30', '2/30', '2/30', '2/30', '1/222', '1/1', '1/444', '2/30', '1/1', '1/444', '1/444', '1/444', '1/222', '1/120', '2/30', '2/30', '1/120', '1/120', '2/30', '2/30', '2/30', '2/30', '1/222', '1/1'],
                   'Lenkungsmethode': [0.0, 0.0, 0.0, 33.0, 33.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 33.0, 0.0, 0.0, 0.0, 20.0, 20.0, 20.0, 33.0, 33.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],
                   'Merkmalsgewichtung': [0, 0, 0, 'HM', 'HM', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'HM', 'HM', 0, 0, 0, 0, 0, 0]
                  }

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/prediction_results', methods=['GET', 'POST'])
def prediction_results():
    global results
    global predictionInput
    global colsToPredict
    if request.method == 'POST':
        import pickle
        import gzip
        predictionInput = request.files['input_prediction']
        predictionInput = pd.read_excel(predictionInput)
        trainData = pd.read_excel('data//traindata.xlsx') 
        with open('misc//mappingInfo.pkl', 'rb') as file:
                mappingInfo = pickle.load(file) 
        for col in colsToPredict:
            with gzip.open('models//{}.pkl'.format(col), 'rb') as file:
                model = pickle.load(file)
            singleColResults = createPrediction(model, predictionInput, col, mappingInfo)  
            results[col] = singleColResults
        print(results)           
                                            
        unique_values = getUniqueValues(trainData)
        featureCount = len(results["Fertigungshilfsmittel"])
        
        return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount = featureCount)
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
            #print(value)
            if key == "Fertigungshilfsmittel":
                list1.append(value)
            if key == "Stichprobenverfahren":
                list2.append(value)
            if key == "Lenkungsmethode":
                list3.append(value)
            if key == "Merkmalsgewichtung":
                list4.append(value)
        predictionOutput = predictionInput
        predictionOutput['Fertigungshilfsmittel'] = list1
        predictionOutput['Stichprobenverfahren'] = list2
        predictionOutput['Lenkungsmethode'] = list3
        predictionOutput['Merkmalsgewichtung'] = list4 

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
    global colsToPredict
    if request.method == 'POST':
        import pickle
        import gzip
        file_training = request.files['input_training']
        trainData = pd.read_excel(file_training)
        modelType = 'rf'
        import pickle
        for col in colsToPredict:
            model = trainNewModel(trainData, modelType, col)  
            print("Accuracy for " + str(col) + ": " + str(model[2]))                                                                                                     
            with gzip.open('models//{}.pkl'.format(col),'wb') as f:
                pickle.dump(model[0],f,protocol=pickle.HIGHEST_PROTOCOL)
        return render_template('index.html')
    return  #diese route wird aktuell nie ohne einen POST trigger aufgerufen, deswegen hier einfach return atm

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    return render_template('monitoring.html')