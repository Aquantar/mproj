Model Training
================

Function: model_training
----------------

Purpose
^^^^^^^^^^^^^^^^
This function is part of routes.py and initializes the re-training of new models when the corresponding button is pressed on the web-UI. It further manages existing models after training is completed.

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
1. Versioning of existing model generations is managed
2. Training data for new model generation is created by combining data used for previous model with saved, currently unused input tuples
3. Training of a model for each desired output feature is initialized by calling :varname:`trainNewModel`, and training progress is tracked
4. Updated monitoring web-page is displayed after successful training

Returns
^^^^^^^^^^^^^^^^
- Re-route to updated :varname:`monitoring.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar, Johannes (Corresponding Web-Overlay :varname:`monitoring.html` built by Johannes)

.. code-block:: python
    
    @app.route('/model_training', methods=['GET', 'POST'])
    def model_training():
        global outputCols
        if request.method == 'POST':
            try:
                dir1 = 'models//model1'
                dir2 = 'models//model2'
                dir3 = 'models//model3'

                #move existing models "down" one folder (versioning)
                for fileName in os.listdir(dir2):
                    shutil.copy(os.path.join(dir2, fileName), dir3)
                for fileName in os.listdir(dir1):
                    shutil.copy(os.path.join(dir1, fileName), dir2)

                #combine existing train data with new rows
                trainData = pd.read_excel('models//model1//currentTrainData.xlsx')
                trainDataNew = pd.read_excel('models//stashedTrainData.xlsx')
                trainData = pd.concat([trainData, trainDataNew]).dropna(how="all")

                #train new models
                accuracyList = []
                progress = 0
                total_steps = len(outputCols) + 2  #steps = col count + preprocessing + metrics

                #preprocessing
                progress += 1
                print(f"Preprocessing abgeschlossen ({progress}/{total_steps})")

                #model training for each output col
                for col in outputCols:
                    model, scaler, conversionMap, accuracy = trainNewModel(trainData, col)
                    dump(model, gzip.open(f'models//model1//{col}.pkl', 'wb'))
                    dump(scaler, open('models//model1//scaler.pkl', 'wb'))
                    dump(conversionMap, open('models//model1//conversionMap.pkl', 'wb'))
                    accuracyList.append(accuracy)
                    progress += 1
                    print(f"Modell für '{col}' trainiert ({progress}/{total_steps})")

                #export training data
                trainData.to_excel("models//model1//currentTrainData.xlsx", index=False)
                pd.DataFrame(columns=list(trainData.columns.values)).to_excel("models//stashedTrainData.xlsx", index=False)

                #refresh model metrics file
                modelMetrics = pd.read_excel('models//modelData.xlsx')
                if not modelMetrics.empty and 'modelID' in modelMetrics.columns:
                    last_model_id = pd.to_numeric(modelMetrics['modelID'], errors='coerce').dropna().astype(int).max()
                    modelID = last_model_id + 1
                else:
                    modelID = 1  #start from 1 if file is empty or column missing
                newrow = [modelID, datetime.today().strftime('%Y-%m-%d')] + accuracyList + [0, 0, 0]
                modelMetrics.loc[len(modelMetrics)] = newrow
                modelMetrics.to_excel("models//modelData.xlsx", index=False)

                progress += 1
                print(f"Modellmetriken aktualisiert ({progress}/{total_steps})")

                #prepare loading of monitoring page
                #load current model metrics
                accuracyData = [
                    [float(i) for i in modelMetrics['accuracy_1'].tolist()],
                    [float(i) for i in modelMetrics['accuracy_2'].tolist()],
                    [float(i) for i in modelMetrics['accuracy_3'].tolist()]
                ]
                last_row = modelMetrics.iloc[-1]
                #load relevant data about current model
                last_row = modelMetrics.iloc[-1]
                predictionStats = {
                    'totalPredictions': int(last_row['totalPredictions']),
                    'predictionChanged': int(last_row['predictionChanged']),
                    'predictionChangeRatio': f"{float(last_row['predictionChangeRatio']) * 100:.2f}%"
                }
                modelIDs = modelMetrics['modelID'].tolist()

                #output monitoring page
                return render_template("monitoring.html", accuracyData=accuracyData, modelIDs=modelIDs, predictionStats=predictionStats)

            except Exception as e:
                print(f"Fehler beim Modelltraining: {e}")
                flash(f"Fehler beim Modelltraining: {e}")
                return redirect(url_for('stasheddata'))
        return redirect(url_for('stasheddata'))

Function: trainNewModel
----------------

Purpose
^^^^^^^^^^^^^^^^
This function fully delegates the training of new predictive model for a single desired output feature, including data preprocessing, model training, and final model selection.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`outputFeature` (string): The feature to be predicted based on input data
- :varname:`trainData` (dataframe): The set of raw training data

Process
^^^^^^^^^^^^^^^^
1. Data Pre-Processing:
    - Function :varname:`prepareRawData` is called, which cleans the training data before further processing
    - Conversion Map Creation: A dictionary that maps each unique value in the training data to a number which is unique within that feature column is created, and the training data is translated into a numeric form using this dictionary
    - Training/Testing Split: The data is split into a training/testing set at an 80/20 ratio, and is further divided into input features and a desired output feature, resulting in :varname:`X_train`, :varname:`X_test`, :varname:`y_train`, :varname:`y_test`
    - Input Feature Scaling: Input features are scaled to values between 0 and 1
2. Model Training:
    - Models using each of the four selected algorithms are trained using the prepared training data through the functions :varname:`randomForest`, :varname:`knn`, :varname:`svm`, and :varname:`neuralNetwork`
    - The best performing models from each algorithm are compared, and the single model with the highest :varname:`accuracy_score` is selected as the final model for the currently desired output feature

Returns
^^^^^^^^^^^^^^^^
- :varname:`res[0]` : The selected model
- :varname:`scaler` : The scaler built for model training
- :varname:`conversionMap` (dictionary): The dictionary which contains the built mapping between text values in the original input data and the numeric values used in training
- :varname:`res[2]` (float): The accuracy of the selected model

Notes
^^^^^^^^^^^^^^^^
- The built scaler as well as conversion map are saved after model training to be used when predicting new values with that pre-trained model
- Built by: Serdar

.. code-block:: python

    def trainNewModel(trainData, outputFeature): 
        trainData = prepareRawData(trainData) #prepare raw data for model training

        #create conversion map
        conversionMap = dict()
        for col in allCols:
            if col in trainData.columns:
                conversionOutput = convertTextColumnToNumbers(trainData, col)
                trainData = conversionOutput[0]
                trainData[col] = pd.to_numeric(trainData[col])
                conversionMap[col] = conversionOutput[1]

        #create split
        X = trainData.drop(outputCols, axis=1).values.tolist()
        y = trainData[outputFeature].values.tolist()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        #scale data
        scaler = MinMaxScaler()
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)
        
        #train models
        modelDict = {}
        modelDict["RF"] = randomForest(X_train, X_test, y_train, y_test)
        print("Accuracy for " + str(outputFeature) + " (RF): " + str(modelDict["RF"][2]))   
        modelDict["KNN"] = knn(X_train, X_test, y_train, y_test)
        print("Accuracy for " + str(outputFeature) + " (KNN): " + str(modelDict["KNN"][2]))      
        modelDict["SVM"] = svm(X_train, X_test, y_train, y_test)
        print("Accuracy for " + str(outputFeature) + " (SVM): " + str(modelDict["SVM"][2]))  
        modelDict["MLP"] = neuralNetwork(X_train, X_test, y_train, y_test)
        print("Accuracy for " + str(outputFeature) + " (MLP): " + str(modelDict["MLP"][2]))  

        #select model with highest accuracy
        keySelected = "RF"
        for key, value in modelDict.items():
            if value[2] > modelDict[keySelected][2]:
                keySelected = key
        
        print("Selected model: " + str(keySelected))
        res = modelDict[keySelected]   

        return res[0], scaler, conversionMap, res[2]

Function: prepareRawData
----------------

Purpose
^^^^^^^^^^^^^^^^
This function cleans a dataframe which contains raw data before use in model training or output feature prediction

Parameters
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): The set of raw training data to be cleaned

Process
^^^^^^^^^^^^^^^^
1. Qualitative component characteristics are removed, as only quantitative characteristics are predictable
2. The data column 'Prüfmerkmal_Text' is cleaned and unnecessary suffixes are removed
3. Unused columns are removed
4. Empty cells are filled with '0'
5. Values which should be numeric are correctly formatted
6. Dataframe is converted to string type

Returns
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): The set of data after pre-processing is completed

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

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

        #wandle alle spalten in string um
        data = data.astype(str)

        return data

Function: convertTextColumnToNumbers
----------------

Purpose
^^^^^^^^^^^^^^^^
This function creates a corresponding number for each unique value in a dataframe column in order to create the conversion map built during model training, and replaces the original values within that column with their corresponding number. A dictionary which maps each original value to a specific number is used at a later point to re-convert numeric values to their original form.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): The set of data to be used for training
- :varname:`colname` (string): The name of the column of which the values are to be converted into numeric values

Process
^^^^^^^^^^^^^^^^
1. For each unique value within the selected column, an ascending number is chosen and the value-number pairs are saved
2. All values within the selected column are replaced by their corresponding number

Returns
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): The set of data with numeric values in the selected column
- :varname:`map_uniqueValues` (dictionary): The dictionary containing the different value-number pairs

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

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

Function: randomForest
----------------

Purpose
^^^^^^^^^^^^^^^^
This function trains a model using :varname:`RandomForestClassifier` which is part of the :varname:`sklearn.ensemble` package.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`X_train` (dataframe): Input features used for model training
- :varname:`X_test` (dataframe): Input features used for model validation
- :varname:`y_test` (dataframe): Output features used for model training
- :varname:`y_test` (dataframe):Output features used for model validation

Process
^^^^^^^^^^^^^^^^
1. Model is created and fitted on training data
2. A set of predictions is performed using :varname:`X_test`. The results are compared with :varname:`y_test`, and an :varname:`accuracy_score` is calculated

Returns
^^^^^^^^^^^^^^^^
- :varname:`model`: The trained model
- :varname:`y_pred` (dataframe): The dataframe which contains the predicted values for validation purposes
- :varname:`accuracy` (float): The resulting model accuracy

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

    def randomForest(X_train, X_test, y_train, y_test):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score

        model = RandomForestClassifier(criterion='entropy')
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

Function: knn
----------------

Purpose
^^^^^^^^^^^^^^^^
This function trains a model using :varname:`KNeighborsClassifier` which is part of the :varname:`sklearn.neighbors` package.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`X_train` (dataframe): Input features used for model training
- :varname:`X_test` (dataframe): Input features used for model validation
- :varname:`y_test` (dataframe): Output features used for model training
- :varname:`y_test` (dataframe):Output features used for model validation

Process
^^^^^^^^^^^^^^^^
1. A series of models is trained using :varname:`GridSearchCV`, testing a range of values for the parameters :varname:`n_neighbors` and :varname:`weights`
1. The set of best-performing parameters is selected to re-create the final model and fit it on used data
2. A set of predictions is performed using :varname:`X_test`. The results are compared with :varname:`y_test`, and an :varname:`accuracy_score` is calculated

Returns
^^^^^^^^^^^^^^^^
- :varname:`model`: The trained model
- :varname:`y_pred` (dataframe): The dataframe which contains the predicted values for validation purposes
- :varname:`accuracy` (float): The resulting model accuracy

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

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

Function: svm
----------------

Purpose
^^^^^^^^^^^^^^^^
This function trains a model using :varname:`SVC` which is part of the :varname:`sklearn.svm` package.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`X_train` (dataframe): Input features used for model training
- :varname:`X_test` (dataframe): Input features used for model validation
- :varname:`y_test` (dataframe): Output features used for model training
- :varname:`y_test` (dataframe):Output features used for model validation

Process
^^^^^^^^^^^^^^^^
1. A series of models is trained using :varname:`GridSearchCV`, testing a range of values for the parameter :varname:`C`
1. The set of best-performing parameters is selected to re-create the final model and fit it on used data
2. A set of predictions is performed using :varname:`X_test`. The results are compared with :varname:`y_test`, and an :varname:`accuracy_score` is calculated

Returns
^^^^^^^^^^^^^^^^
- :varname:`model`: The trained model
- :varname:`y_pred` (dataframe): The dataframe which contains the predicted values for validation purposes
- :varname:`accuracy` (float): The resulting model accuracy

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

    def svm(X_train, X_test, y_train, y_test):
        from sklearn.svm import SVC
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import GridSearchCV

        param_grid = {'C': [4, 8, 16, 32, 48, 64, 80]}
        grid = GridSearchCV(SVC(), param_grid, refit = True, verbose = 3,n_jobs=-1) 
        grid.fit(X_train, y_train) 

        model = SVC(C=grid.best_params_["C"])
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        return model, y_pred, accuracy

Function: neuralNetwork
----------------

Purpose
^^^^^^^^^^^^^^^^
This function trains a model using :varname:`MLPClassifier` which is part of the :varname:`sklearn.neural_network` package.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`X_train` (dataframe): Input features used for model training
- :varname:`X_test` (dataframe): Input features used for model validation
- :varname:`y_test` (dataframe): Output features used for model training
- :varname:`y_test` (dataframe):Output features used for model validation

Process
^^^^^^^^^^^^^^^^
1. A series of models is trained using :varname:`GridSearchCV`, testing a range of values for the parameter :varname:`alpha`
1. The set of best-performing parameters is selected to re-create the final model and fit it on used data
2. A set of predictions is performed using :varname:`X_test`. The results are compared with :varname:`y_test`, and an :varname:`accuracy_score` is calculated

Returns
^^^^^^^^^^^^^^^^
- :varname:`model`: The trained model
- :varname:`y_pred` (dataframe): The dataframe which contains the predicted values for validation purposes
- :varname:`accuracy` (float): The resulting model accuracy

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

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