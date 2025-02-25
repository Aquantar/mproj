from app import app, inputCols, outputCols, allCols
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def createPrediction(model, predData, outputFeature, conversionMap, scaler): 
    predData = convertPredDataToDataframe(predData)
    predData = prepareRawData(predData)
    #predData = predData.drop(outputCols, axis=1)
    for index, row in predData.iterrows():
        for key, value in conversionMap.items():
            if key in predData.columns:
                try:
                    predData.at[index, key]=value[row[key]]
                except:
                    currentDict = conversionMap[key]
                    highestValue = 0
                    for key2, value2 in currentDict.items():
                        if value2 > highestValue:
                            highestValue = value2
                    highestValue += 1
                    currentDict[row[key]] = highestValue
                    conversionMap[key] = currentDict
                    predData.at[index, key]=value[row[key]]
    predData = predData.values.tolist()
    predData = scaler.transform(predData)
    preds = model.predict(predData)
    
    predictions_text = []
    for idx, pred in enumerate(preds):
        if outputFeature in conversionMap:
            mapping = conversionMap[outputFeature]
            for key, val in mapping.items():
                if val == preds[idx]:
                    predictions_text.append(key)
        else:
            predictions_text.append(str(pred))

    return predictions_text

def trainNewModel(trainData, outputFeature): 
    trainData = prepareRawData(trainData)

    conversionMap = dict()
    for col in allCols:
        if col in trainData.columns:
            conversionOutput = convertTextColumnToNumbers(trainData, col)
            trainData = conversionOutput[0]
            trainData[col] = pd.to_numeric(trainData[col])
            conversionMap[col] = conversionOutput[1]

    X = trainData.drop(outputCols, axis=1).values.tolist()
    y = trainData[outputFeature].values.tolist()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    
    res = randomForest(X_train, X_test, y_train, y_test)

    print("Accuracy for " + str(outputFeature) + ": " + str(res[2]))       

    return res[0], scaler, conversionMap

def randomForest(X_train, X_test, y_train, y_test):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    model = RandomForestClassifier(criterion='entropy')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def prepareRawData(data):
    #entferne qualitative merkmale
    if 'Qualitatives_Merkmal' in data.columns:
        data.drop(data[data['Qualitatives_Merkmal'] == "X"].index, inplace = True)
        data = data.drop(['Qualitatives_Merkmal'], axis=1)

    #fülle prüfmerkmals-text mit werten aus anderer spalte falls nötig
    if 'Produktmerkmal_Text' in data.columns:
        for index, row in data.iterrows():
            newval = str(row['Produktmerkmal_Text']).split(" ")
            newval = newval[0]
            data.at[index,'Produktmerkmal_Text']=newval

    #entferne nicht verwendete spalten
    for col in data.columns:
        if col not in allCols:
            data = data.drop([col], axis=1)

    #fülle leere zellen mit 0
    data = data.fillna(0)

    #formatiere zahlen zu korrektem dezimalformat (, statt .) und wandle in float um

    for index, row in data.iterrows():
        data.at[index,'Spezifikation']=str(row['Spezifikation']).replace(',','.')
    for index, row in data.iterrows():
        if " " in str(row['Spezifikation']):
            data.at[index,'Spezifikation']=str(row['Spezifikation']).split(" ")[0]
    for index, row in data.iterrows():
        data.at[index,'Spezifikation']=float(row['Spezifikation'])
    for index, row in data.iterrows():
        data.at[index,'Oberer_Grenzwert']=str(row['Oberer_Grenzwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Oberer_Grenzwert']=float(row['Oberer_Grenzwert'])
    for index, row in data.iterrows():
        data.at[index,'Unterer_Grenzwert']=str(row['Unterer_Grenzwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Unterer_Grenzwert']=float(row['Unterer_Grenzwert'])

    #wandle zellen "Unterer Grenzwert" und "Oberer Grenzwert" in differenzen statt absolute zahlen um
    list_lower = []
    list_upper = []
    for index, row in data.iterrows():
        list_lower.append(row['Spezifikation']-row['Unterer_Grenzwert'])
        list_upper.append(row['Oberer_Grenzwert']-row['Spezifikation'])
    data['Unterer_Grenzwert'] = list_lower
    data['Oberer_Grenzwert'] = list_upper

    #wandle spalte "nachkommastellen" in integer um
    #data['Nachkommastellen'] = data['Nachkommastellen'].astype(int)

    #wandle alle spalten in string um
    data = data.astype(str)

    return data

def convertTextColumnToNumbers(data, colname):
    #wandelt eine spalte mit textwerten in einem dataframe in zahlen um und speichert text/zahlenpaare für spätere rückwandlung
    list_uniqueValues = data[colname].unique()
    map_uniqueValues = dict()
    intTemp = 1
    for element in list_uniqueValues:
        map_uniqueValues[element] = intTemp
        intTemp+=1
    for index, row in data.iterrows():
        data.at[index,colname]=map_uniqueValues.get(row[colname])
    return data, map_uniqueValues

def getUniqueValues(data):
    uniqueVals = {}
    for col in outputCols:    
        uniqueList =  data[col].unique()
        print(uniqueList)
        uniqueList = [str(r) for r in uniqueList]    
        uniqueVals[col] = uniqueList
    return uniqueVals

def convertPredDataToDataframe(data):
    pd.set_option('display.max_columns', None)
    dataAll = pd.read_excel(data)
    data = pd.read_excel(data, skiprows=11)
    data = data.drop(data.columns[[0, 1, 2, 3, 4, 5, 8, 9, 12, 14, 15, 16, 17, 18]],axis=1)
    data = data.rename(columns={"Unnamed: 6": "Produktmerkmal", "Unnamed: 7": "Produktmerkmal_Text", "Unnamed: 10": "Spezifikation", "Unnamed: 11": "Unterer_Grenzwert", "Unnamed: 13": "Oberer_Grenzwert"})
    data = data[data['Produktmerkmal'].notna()]
    
    prozesselement = dataAll.iloc[11,2]
    maschine = dataAll.iloc[11,5]
    arbeitsplatz = dataAll.iloc[2,6]

    data["Prozesselement"] = prozesselement
    data["Maschine"] = maschine
    data["Arbeitsplatz"] = arbeitsplatz.split("\n")[1]
    print(data)

    return data
