from app import app, results
from flask import Flask, render_template, request, url_for, redirect, make_response
from app.functions import *
from io import BytesIO
import xlsxwriter

optionen = ["Option 1", "Option 2", "Option 3", "Option 4"]
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
    if request.method == 'POST':
        file_prediction = request.files['input_prediction']
        
        trainData = pd.read_excel('data//traindata.xlsx')
        predData = pd.read_excel(file_prediction)
        modelType = 'rf'
        #results = createPrediction(trainData, predData, modelType)         IST AUSKOMMENTIERT WEIL ES AKTUELL ZU LANGE DAUERT
                                                                             #FÜRS ERSTE EINFACH DIESE RESULTS BENUTZEN, SIND DIE DUMMY WERTE VON OBEN
        
        results = predictionDummy                                          
        unique_values = getUniqueValues(trainData)
        featureCount = len(results["Fertigungshilfsmittel"])
        
        return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount = featureCount)
    return

@app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
def prediction_results_confirmed():
    global results
    if request.method == 'POST':
        choicesOutput = request.form
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        for key, value in choicesOutput.items(multi=True):
            if key == "Fertigungshilfsmittel":
                list1.append(value)
            if key == "Stichprobenverfahren":
                list2.append(value)
            if key == "Lenkungsmethode":
                list3.append(value)
            if key == "Merkmalsgewichtung":
                list4.append(value)
        outputForm = pd.read_excel('data//testdata_control.xlsx')
        outputForm['Fertigungshilfsmittel'] = list1
        outputForm['Stichprobenverfahren'] = list2
        outputForm['Lenkungsmethode'] = list3
        outputForm['Merkmalsgewichtung'] = list4 

        sio = BytesIO()
        outputName = "output"
        writerImportsheet = pd.ExcelWriter("{}.xlsx".format(outputName), engine="xlsxwriter")
        outputForm.to_excel(writerImportsheet, sheet_name="Sheet1", index=False)
        workbook = xlsxwriter.Workbook(sio)
        sheet = workbook.add_worksheet(u'sheet1')

        #Header
        columns = list(outputForm.columns.values) 
        iter = 0
        for col in columns:
            sheet.write(0, iter, col)
            full_column = outputForm.iloc[:, iter]
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
    return

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('monitoring'))
    # show the form, it wasn't submitted
    return render_template('monitoring.html')