import pandas as pd
from sklearn.model_selection import train_test_split

def createPrediction(trainData, predData, modelType): 

    trainData_processed = prepareRawData(trainData)
    predData_processed = prepareRawData(predData)

    #konvertiere textwerte in angegebenen spalten zu zahlen, speichere werte für spätere rück-umwandlung in mappingInfo
    print("starting to map")
    combinedData = pd.concat([trainData_processed, predData_processed])
    columnsToConvert = ['Prüfmerkmal_Text', 'Fertigungshilfsmittel', 'Merkmalsgewichtung', 'Maßeinheit', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']
    mappingInfo = dict()
    for col in columnsToConvert:
        if col in combinedData.columns:
            temp = convertTextColumnToNumbers(combinedData, col)
            mappingInfo[col] = temp[1]

    for index, row in trainData_processed.iterrows():
            for key, value in mappingInfo.items():
                try:
                    trainData_processed.at[index, key]=value[row[key]]
                except:
                    print(key)
                    print(row[key])

    for index, row in predData_processed.iterrows():
        for key, value in mappingInfo.items():
            try:
                predData_processed.at[index, key]=value[row[key]]
            except:
                print(key)
                print(row[key])

    colsToClassify = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']
    results = []
    resultsDict = {}
    for col in colsToClassify:
        X_train = trainData_processed.drop(colsToClassify, axis=1)
        X_test = predData_processed.drop(colsToClassify, axis=1)
        y_train = trainData_processed[col].astype(int)
        y_test = predData_processed[col].astype(int)

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        if modelType == 'rf':
            res = randomForest(X_train, X_test, y_train, y_test)
        elif modelType == 'svm':
            res = supportVectorMachine(X_train, X_test, y_train, y_test)
        elif modelType == 'neuralNetwork':
            res = neuralNetwork(X_train, X_test, y_train, y_test)
        elif modelType == 'naiveBayes':
            res = naiveBayes(X_train, X_test, y_train, y_test)
        elif modelType == 'knn':
            res = kNearestNeighbor(X_train, X_test, y_train, y_test)

        preds = res[1]
        preds_text = []
        for idx, pred in enumerate(preds):
            mapping = mappingInfo[col]
            for key, val in mapping.items():
                if val == preds[idx]:
                    preds_text.append(key)
        res = list(res)
        res.append(preds_text)
        res = tuple(res)

        resultsDict[col] = preds_text

    return resultsDict


def createPredictionBackup(trainData, predData, modelType): 

    trainData_processed = prepareRawData(trainData)
    predData_processed = prepareRawData(predData)

    #konvertiere textwerte in angegebenen spalten zu zahlen, speichere werte für spätere rück-umwandlung in mappingInfo
    print("starting to map")
    combinedData = pd.concat([trainData_processed, predData_processed])
    columnsToConvert = ['Prüfmerkmal_Text', 'Fertigungshilfsmittel', 'Merkmalsgewichtung', 'Maßeinheit', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']
    mappingInfo = dict()
    for col in columnsToConvert:
        if col in combinedData.columns:
            temp = convertTextColumnToNumbers(combinedData, col)
            mappingInfo[col] = temp[1]

    for index, row in trainData_processed.iterrows():
            for key, value in mappingInfo.items():
                try:
                    trainData_processed.at[index, key]=value[row[key]]
                except:
                    print(key)
                    print(row[key])

    for index, row in predData_processed.iterrows():
        for key, value in mappingInfo.items():
            try:
                predData_processed.at[index, key]=value[row[key]]
            except:
                print(key)
                print(row[key])

    colsToClassify = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']
    results = []
    for col in colsToClassify:
        X_train = trainData_processed.drop(colsToClassify, axis=1)
        X_test = predData_processed.drop(colsToClassify, axis=1)
        y_train = trainData_processed[col].astype(int)
        y_test = predData_processed[col].astype(int)

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        if modelType == 'rf':
            res = randomForest(X_train, X_test, y_train, y_test)
        elif modelType == 'svm':
            res = supportVectorMachine(X_train, X_test, y_train, y_test)
        elif modelType == 'neuralNetwork':
            res = neuralNetwork(X_train, X_test, y_train, y_test)
        elif modelType == 'naiveBayes':
            res = naiveBayes(X_train, X_test, y_train, y_test)
        elif modelType == 'knn':
            res = kNearestNeighbor(X_train, X_test, y_train, y_test)

        preds = res[1]
        preds_text = []
        for idx, pred in enumerate(preds):
            mapping = mappingInfo[col]
            for key, val in mapping.items():
                if val == preds[idx]:
                    preds_text.append(key)
        res = list(res)
        res.append(preds_text)
        res = tuple(res)

        results.append(res)
    return results


def createPrediction2(trainData, predData, modelType): 

    trainData_processed = prepareRawData(trainData)
    predData_processed = prepareRawData(predData)

    #konvertiere textwerte in angegebenen spalten zu zahlen, speichere werte für spätere rück-umwandlung in mappingInfo
    print("starting to map")
    combinedData = pd.concat([trainData_processed, predData_processed])
    columnsToConvert = ['Prüfmerkmal_Text', 'Fertigungshilfsmittel', 'Merkmalsgewichtung', 'Maßeinheit', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']
    mappingInfo = dict()
    for col in columnsToConvert:
        if col in combinedData.columns:
            temp = convertTextColumnToNumbers(combinedData, col)
            mappingInfo[col] = temp[1]

    for index, row in trainData_processed.iterrows():
            for key, value in mappingInfo.items():
                try:
                    trainData_processed.at[index, key]=value[row[key]]
                except:
                    print(key)
                    print(row[key])

    for index, row in predData_processed.iterrows():
        for key, value in mappingInfo.items():
            try:
                predData_processed.at[index, key]=value[row[key]]
            except:
                print(key)
                print(row[key])

    colsToClassify = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']
    results = []
    for col in colsToClassify:
        X_train = trainData_processed.drop(colsToClassify, axis=1)
        X_test = predData_processed.drop(colsToClassify, axis=1)
        y_train = trainData_processed[col].astype(int)
        y_test = predData_processed[col].astype(int)

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        if modelType == 'rf':
            res = randomForest(X_train, X_test, y_train, y_test)
        elif modelType == 'svm':
            res = supportVectorMachine(X_train, X_test, y_train, y_test)
        elif modelType == 'neuralNetwork':
            res = neuralNetwork(X_train, X_test, y_train, y_test)
        elif modelType == 'naiveBayes':
            res = naiveBayes(X_train, X_test, y_train, y_test)
        elif modelType == 'knn':
            res = kNearestNeighbor(X_train, X_test, y_train, y_test)

        preds = res[1]
        preds_text = []
        for idx, pred in enumerate(preds):
            mapping = mappingInfo[col]
            for key, val in mapping.items():
                if val == preds[idx]:
                    preds_text.append(key)
        res = list(res)
        res.append(preds_text)
        res = tuple(res)

        results.append(res)
    return results

def prepareRawData(data):
    usedCols = ['Prüfmerkmal_Text', 'Fertigungshilfsmittel', 'Sollwert', 'Merkmalsgewichtung', 'Maßeinheit', 'Oberer_Grenzwert', 'Unterer_Grenzwert', 'Nachkommastellen', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'Plangruppe', 'Knotenplan', 'Verbindung', 'Arbeitsplatz', 'Beschreibung_Vorgang']

    #entferne qualitative merkmale
    if 'Qualitatives_Merkmal' in data.columns:
        data.drop(data[data['Qualitatives_Merkmal'] == "X"].index, inplace = True)
        data = data.drop(['Qualitatives_Merkmal'], axis=1)

    #fülle prüfmerkmals-text mit werten aus anderer spalte falls nötig
    if 'Prüfmerkmal_Text_Voll' in data.columns:
        for index, row in data.iterrows():
            #if row['Prüfmerkmal_Text'].isna():
            if not isinstance(row['Prüfmerkmal_Text'], str):
                newval = str(row['Prüfmerkmal_Text_Voll']).split(" ")
                newval = newval[0]
                data.at[index,'Prüfmerkmal_Text']=newval
            else:
                pass
        data = data.drop(['Prüfmerkmal_Text_Voll'], axis=1)

    #entferne nicht verwendete spalten
    for col in data.columns:
        if col not in usedCols:
            data = data.drop([col], axis=1)

    #fülle leere zellen mit 0
    data = data.fillna(0)

    #formatiere zahlen zu korrektem dezimalformat (, statt .) und wandle in float um
    for index, row in data.iterrows():
        data.at[index,'Sollwert']=str(row['Sollwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Sollwert']=float(row['Sollwert'])
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
        list_lower.append(row['Sollwert']-row['Unterer_Grenzwert'])
        list_upper.append(row['Oberer_Grenzwert']-row['Sollwert'])
    data['Unterer_Grenzwert'] = list_lower
    data['Oberer_Grenzwert'] = list_upper

    #wandle spalte "nachkommastellen" in integer um
    data['Nachkommastellen'] = data['Nachkommastellen'].astype(int)

    return data

def convertTextColumnToNumbers(data, colname):
    list_uniqueValues = data[colname].unique()
    map_uniqueValues = dict()
    intTemp = 1
    for element in list_uniqueValues:
        map_uniqueValues[element] = intTemp
        intTemp+=1
    for index, row in data.iterrows():
        data.at[index,colname]=map_uniqueValues.get(row[colname])
    return data, map_uniqueValues


def randomForest(X_train, X_test, y_train, y_test):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    model = RandomForestClassifier(criterion='entropy')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def supportVectorMachine(X_train, X_test, y_train, y_test):
    from sklearn.svm import SVC
    from sklearn.multiclass import OneVsOneClassifier
    from sklearn.metrics import accuracy_score

    model = OneVsOneClassifier(SVC(C=12))
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def neuralNetwork(X_train, X_test, y_train, y_test):
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import accuracy_score

    model = MLPClassifier(solver='adam', max_iter=2000, alpha=0.001,
                    hidden_layer_sizes=(15,), random_state=1)
    model.fit(X_train,y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def naiveBayes(X_train, X_test, y_train, y_test):
    from sklearn.naive_bayes import BernoulliNB
    from sklearn.metrics import accuracy_score

    model = BernoulliNB(binarize=True)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def kNearestNeighbor(X_train, X_test, y_train, y_test):
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score

    model = KNeighborsClassifier(n_neighbors=40, weights="distance", algorithm="ball_tree")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def getUniqueValues(trainData):
    uniqueVals = {}
    cols = ['Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']
    for col in cols:     
        uniqueVals[col] = trainData[col].unique()
    return uniqueVals