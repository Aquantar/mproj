import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def classifyData(classifier, colToClassify):
    data = pd.read_excel('data\input_test.xlsx')
    data = preprocessor(data)

    #split data into training/testing set and scale values
    X = data.drop(['Text zum Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung']  , axis=1)
    y = data[colToClassify].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    if classifier == 'rf':
        classificationResults = randomForest(X_train, X_test, y_train, y_test)
    elif classifier == 'svm':
        classificationResults = supportVectorMachine(X_train, X_test, y_train, y_test)
    elif classifier == 'neuralNetwork':
        classificationResults = neuralNetwork(X_train, X_test, y_train, y_test)
    elif classifier == 'naiveBayes':
        classificationResults = naiveBayes(X_train, X_test, y_train, y_test)
    elif classifier == 'knn':
        classificationResults = kNearestNeighbor(X_train, X_test, y_train, y_test)
    else:
        print('invalid classifier')
        classificationResults = []

    return classificationResults

def preprocessor(data):
    #entferne alle qualitativen Merkmale
    data.drop(data[data['Qualitat. Merkmal'] == "X"].index, inplace = True)

    #Fülle Kurztext Prüfmerkmal mit Werten aus vorherigen Spalte minus Maßangaben
    for index, row in data.iterrows():
        newval = str(row['Kurztext Prüfmerkmal']).split(" ")
        newval = newval[0]
        data.at[index,'Kurztext Prüfmerkmal.1']=newval

    #entferne nicht gebrauchte spalten
    data = data.drop(['Prüfmerkmal'], axis=1)
    data = data.drop(['Kurztext Prüfmerkmal'], axis=1)
    data = data.drop(['Prüfmittel'], axis=1)
    data = data.drop(['Qualitat. Merkmal'], axis=1)
    data = data.drop(['Kurztext zum Stichprobenverfahren'], axis=1)
    #data = data.drop(['Plangruppe'], axis=1)

    #fülle leere Zellen mit 0
    data = data.fillna(0)

    #Formatiere Zahlen zu richtigem Dezimalformat (, statt .) und wandle in Zahl um
    for index, row in data.iterrows():
        data.at[index,'Sollwert']=str(row['Sollwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Sollwert']=float(row['Sollwert'])

    for index, row in data.iterrows():
        data.at[index,'Oberer Grenzwert']=str(row['Oberer Grenzwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Oberer Grenzwert']=float(row['Oberer Grenzwert'])

    for index, row in data.iterrows():
        data.at[index,'Unterer Grenzwert']=str(row['Unterer Grenzwert']).replace(',','.')
    for index, row in data.iterrows():
        data.at[index,'Unterer Grenzwert']=float(row['Unterer Grenzwert'])

    #Wandle Zellen "Unterer Grenzwert" und "Oberer Grenzwert" in Differenzen statt absolute Zahlen um
    list_lower = []
    list_upper = []
    for index, row in data.iterrows():
        list_lower.append(row['Sollwert']-row['Unterer Grenzwert'])
        list_upper.append(row['Oberer Grenzwert']-row['Sollwert'])
    data['Unterer Grenzwert'] = list_lower
    data['Oberer Grenzwert'] = list_upper

    data['Nachkommastellen'] = data['Nachkommastellen'].astype(int)

    #Konvertiere Werte in angegebenen Spalten zu Zahlen
    columnsToConvert = ['Kurztext Prüfmerkmal.1', 'Text zum Fertigungshilfsmittel', 'Merkmalsgewichtung', 'Maßeinheit', 'Stichprobenverfahren', 'Vorgang', 'Lenkungsmethode', 'KnotenPlan', 'Plangruppe', 'unnamed', 'Arbeitsplatz', 'Beschreibung Vorgang']
    for col in columnsToConvert:
        data = convertColumnValuesToNumbers(data, col)[0]

    return data


def convertColumnValuesToNumbers(data, colname):
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

    rf = RandomForestClassifier(criterion='entropy')
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return y_pred, accuracy

def supportVectorMachine(X_train, X_test, y_train, y_test):
    from sklearn.svm import SVC
    from sklearn.multiclass import OneVsOneClassifier
    from sklearn.metrics import accuracy_score

    rbf = OneVsOneClassifier(SVC(C=12))
    rbf.fit(X_train, y_train)
    y_pred = rbf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return y_pred, accuracy

def neuralNetwork(X_train, X_test, y_train, y_test):
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import accuracy_score

    clf = MLPClassifier(solver='adam', max_iter=2000, alpha=0.001,
                    hidden_layer_sizes=(15,), random_state=1)
    clf = clf.fit(X_train,y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return y_pred, accuracy

def naiveBayes(X_train, X_test, y_train, y_test):
    from sklearn.naive_bayes import BernoulliNB
    from sklearn.metrics import accuracy_score

    model = BernoulliNB(binarize=True)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return y_pred, accuracy

def kNearestNeighbor(X_train, X_test, y_train, y_test):
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score

    knn = KNeighborsClassifier(n_neighbors=40, weights="distance", algorithm="ball_tree")
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return y_pred, accuracy