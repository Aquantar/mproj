from app import app, inputCols, outputCols, allCols
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def createPrediction(model, predData, outputFeature, conversionMap, scaler): 
    #predData = convertPredDataToDataframe(predData)
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

    #prepare mapping for Lenkungsmethode
    if outputFeature == "Lenkungsmethode":
        mappingFrame = pd.read_excel('data//controlMethod_mappingInfo.xlsx')

    #create probabilityList
    predProbabilities = model.predict_proba(predData)
    probaTuple = []
    for idx, predTuple in enumerate(predProbabilities):
        tuple = []
        for idx2, proba in enumerate(predProbabilities[idx]):
            if outputFeature in conversionMap:
                mapping = conversionMap[outputFeature]
                for key, val in mapping.items():
                    if val == idx2+1:
                        if outputFeature != "Lenkungsmethode":
                            tuple.append([key, str(key) + " (" + str(int(round(proba,2)*100)) + "%)", proba,""])
                        else:
                            desc = mappingFrame.loc[mappingFrame['Lenkungsmethode'] == int(float(key)), 'Beschreibung']
                            if len(desc) > 0:
                                tuple.append([key, str(key) + " (" + str(int(round(proba,2)*100)) + "%)", proba, desc.item() + " (" + str(int(float(key))) + ")" + " (" + str(int(round(proba,2)*100)) + "%)"])
                            else:
                                tuple.append([key, str(key) + " (" + str(int(round(proba,2)*100)) + "%)", proba, str(int(float(key))) + " (" + str(int(round(proba,2)*100)) + "%)"])
            else:
                print("???")
        probaTuple.append(tuple)

    #sort probabilityList
    sortedFull=[]
    for idx,tuple in enumerate(probaTuple):
        probaTupleSorted = []
        for idx2, tuple2 in enumerate(probaTuple[idx]):
            singleTuple = probaTuple[idx][idx2]
            if len(probaTupleSorted) == 0:
                probaTupleSorted.append(singleTuple)
            else:
                probaTupleSorted.append(singleTuple)
                correctOrder = False
                startIndex = len(probaTupleSorted)-1
                while not correctOrder and startIndex!=0:
                    if probaTupleSorted[startIndex][2] > probaTupleSorted[startIndex-1][2]:
                        probaTupleSorted[startIndex-1], probaTupleSorted[startIndex] = probaTupleSorted[startIndex], probaTupleSorted[startIndex-1]
                        startIndex = startIndex-1
                    else:
                        correctOrder = True
        sortedFull.append(probaTupleSorted)
    probaTuple = sortedFull

    return predictions_text, probaTuple

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
    
    modelDict = {}

    modelDict["RF"] = randomForest(X_train, X_test, y_train, y_test)
    print("Accuracy for " + str(outputFeature) + " (RF): " + str(modelDict["RF"][2]))   
    #modelDict["KNN"] = knn(X_train, X_test, y_train, y_test)
    #print("Accuracy for " + str(outputFeature) + " (KNN): " + str(modelDict["KNN"][2]))      
    #modelDict["SVM"] = svm(X_train, X_test, y_train, y_test)
    #print("Accuracy for " + str(outputFeature) + " (SVM): " + str(modelDict["SVM"][2]))  
    #modelDict["MLP"] = neuralNetwork(X_train, X_test, y_train, y_test)
    #print("Accuracy for " + str(outputFeature) + " (MLP): " + str(modelDict["MLP"][2]))  

    keySelected = "RF"
    for key, value in modelDict.items():
        if value[2] > modelDict[keySelected][2]:
            keySelected = key
    
    print("Selected model: " + str(keySelected))
    res = modelDict[keySelected]   

    return res[0], scaler, conversionMap, res[2]

def randomForest(X_train, X_test, y_train, y_test):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score

    model = RandomForestClassifier(criterion='entropy')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def knn(X_train, X_test, y_train, y_test):
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import GridSearchCV

    param_grid = {'n_neighbors': [4, 8, 16, 32, 48, 64, 80],  
                'weights': ['uniform', 'distance']}
    grid = GridSearchCV(KNeighborsClassifier(), param_grid, refit = True, verbose = 3,n_jobs=-1) 
    grid.fit(X_train, y_train) 

    model = KNeighborsClassifier(n_neighbors=grid.best_params_["n_neighbors"], weights=grid.best_params_["weights"], algorithm="ball_tree")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def svm(X_train, X_test, y_train, y_test):
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import GridSearchCV
    #from sklearn.multiclass import OneVsOneClassifier

    param_grid = {'C': [4, 8, 16, 32, 48, 64, 80]}
    grid = GridSearchCV(SVC(), param_grid, refit = True, verbose = 3,n_jobs=-1) 
    grid.fit(X_train, y_train) 

    model = SVC(C=grid.best_params_["C"])
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, y_pred, accuracy

def neuralNetwork(X_train, X_test, y_train, y_test):
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import GridSearchCV
    import numpy as np

    param_grid = {'solver': ['adam'],
        'max_iter': [2000],
        'alpha': 10.0 ** -np.arange(1, 7),
        'hidden_layer_sizes': [(15,)],
        'random_state': [1]
        }
    
    grid = GridSearchCV(MLPClassifier(), param_grid, refit = True, verbose = 3,n_jobs=-1) 
    grid.fit(X_train, y_train) 

    model = MLPClassifier(solver=grid.best_params_["solver"], max_iter=grid.best_params_["max_iter"], alpha=grid.best_params_["alpha"], hidden_layer_sizes=grid.best_params_["hidden_layer_sizes"], random_state=grid.best_params_["random_state"])
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
        #print(uniqueList)
        uniqueList = [str(r) for r in uniqueList]    
        uniqueVals[col] = uniqueList
    return uniqueVals

def convertPredDataToDataframe(data):
    pd.set_option('display.max_columns', None)
    dataAll = pd.read_excel(data)
    data = pd.read_excel(data, skiprows=11)
    data = data.drop(data.columns[[0, 1, 2, 3, 4, 5, 8, 9, 12, 14, 15, 16, 17, 18]],axis=1)

    specificationList = data["Unnamed: 10"].tolist()
    units = []
    for idx, x in enumerate(specificationList):
        try:
            split = x.split(" ")
            specificationList[idx] = split[0]
            units.append(split[1])
        except:
            units.append("")

    data = data.rename(columns={"Unnamed: 6": "Produktmerkmal", "Unnamed: 7": "Produktmerkmal_Text", "Unnamed: 10": "Spezifikation", "Unnamed: 11": "Unterer_Grenzwert", "Unnamed: 13": "Oberer_Grenzwert"})
    data["Masseinheit"] = units
    data = data[data['Produktmerkmal_Text'].notna()]
    


    prozesselement = dataAll.iloc[11,2]
    maschine = dataAll.iloc[11,5]
    arbeitsplatz = dataAll.iloc[2,6]

    data["Prozesselement"] = prozesselement
    data["Maschine"] = maschine
    #data["Arbeitsplatz"] = arbeitsplatz.split("\n")[1]
    #print(data)

    return data