Feature Prediction
=====

Function: prediction_results
----------------

Purpose
^^^^^^^^^^^^^^^^
This function is part of routes.py. After receiving an input in the form of a .xlsx file through the web-UI, it loads relevant items required for output feature prediction and calls :varname:`createPrediction` for each desired output feature type.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`input_prediction`: Input .xlsx file uploaded via web-UI containing raw input data tuples

Process
^^^^^^^^^^^^^^^^
1. Preparation of items required for predicions:
        - Loads the :varname:`conversionMap` built during model training
        - Loads the :varname:`scaler` built during model training
2. Initial Preparation: :varname:`convertPredDataToDataframe` is called in order to convert the initial input file into a dataframe suitable for pre-processing
3. Delegation of output feature prediction: For each desired output feature, the correct model is loaded and :varname:`createPrediction` is called
4. Resulting output features for each feature type are added to input and visualized on the web-UI

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`prediction_results.html`, displaying input featurs and the corresponding predicted output features on the web-UI

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar (Corresponding Web-Overlay :varname:`prediction_results.html` built by Serdar, Johannes)

.. code-block:: python

    @app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
    def prediction_results():
        global results
        global outputCols
        global predInputFormatted
        global originalInputFile
        if request.method == 'POST':
            originalInputFile = request.files['input_prediction']
            conversionMap = load(open('models//model1//conversionMap.pkl', 'rb'))   #load conversion map of current model
            scaler = load(open('models//model1//scaler.pkl', 'rb')) #load scaler of current model
            predInputFormatted = convertPredDataToDataframe(originalInputFile) #take input file, convert into dataframe to be used for predictions
            originalInputFile = load_workbook(originalInputFile) #saving original input as workbook in this var to re-output it including predicion results later
            probaDict = {}
            for col in outputCols:  #perform prediction for each desired predicted feature
                model = load(gzip.open('models//model1//{}.pkl'.format(col), 'rb')) #load current model
                singleColResults, probaTuple = createPrediction(model, predInputFormatted, col, conversionMap, scaler) #create predictions for current feature
                results[col] = singleColResults #add predictions to results dict
                probaDict[col] = probaTuple #add probability values to probaDict
            for key, value in results.items():  #add output features to input
                predInputFormatted[key] = value

            unique_values = getUniqueValues(pd.read_excel('models//model1//currentTrainData.xlsx')) #extract all unique values for display purposes
            
            return render_template('prediction_results.html', uniqueVals=unique_values, results=results, featureCount=len(predInputFormatted.index), predictionInput=predInputFormatted.to_dict(orient='records'), probaDict=probaDict)
        return

Function: prediction_results_confirmed
----------------

Purpose
^^^^^^^^^^^^^^^^
This function is part of routes.py. After prediction results have been validated by a human via web-UI following the function :varname:`prediction_results`, any modifications done are applied and documented before a final output file is streamed outwards. Further, new tuples found within the input data that do not exist within the training data of the current model are saved for re-training in the future

Parameters
^^^^^^^^^^^^^^^^
- :varname:`choicesOutput` : request form containing validated and possibly manipulated prediction data after human interaction via Web-UI

Process
^^^^^^^^^^^^^^^^
1. Preparation and output of validated results
    - Any human changes done via web-UI during the control step are implemented in the output dataframe
    - Input tuples are combined with their corresponding output features
2. Amount of human changes to results are recorded to model metrics
3. File :varname:`stashedTrainData` is updated with input tuples that do not exist in current training data
4. Download of final output file is initiated

Returns
^^^^^^^^^^^^^^^^
- Final output file in the form of a streamed .xlsx file

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar, Johannes (Corresponding Web-Overlay :varname:`prediction_results.html` built by Serdar, Johannes)

.. code-block:: python

    @app.route('/prediction_results_confirmed', methods=['GET', 'POST'])
    def prediction_results_confirmed():
        global results
        global predInputFormatted
        global originalInputFile
        global outputCols
        if request.method == 'POST':
            #replace predicted values with modified ones from results form
            choicesOutput = request.form
            outputDict = {}
            for key, value in choicesOutput.items(multi=True):
                valTrimmed = re.sub(r' \(\d+%\)', '', value)
                try:
                    listTemp = outputDict[key]
                except:
                    listTemp = []
                listTemp.append(valTrimmed)
                outputDict[key] = listTemp

            #check differences in pre and post human monitoring, and document
            totalVals = 0
            diffSelection = 0
            for key, item in outputDict.items():
                listPre = results[key]
                listPost = outputDict[key]
                totalVals = totalVals + len(listPre)
                for idx, val in enumerate(listPre):
                    if listPre[idx] != listPost[idx]:
                        diffSelection+=1
            modelMetrics = pd.read_excel('models//modelData.xlsx')
            lastrow = modelMetrics.iloc[-1].tolist()
            lastrow[5] = int(lastrow[5]) + totalVals
            lastrow[6] = int(lastrow[6]) + diffSelection
            lastrow[7] = lastrow[6]/lastrow[5]
            modelMetrics.iloc[-1] = lastrow
            modelMetrics.to_excel("models//modelData.xlsx", index=False)

            #combine predictions with inputs
            predictionOutput = predInputFormatted
            predictionOutput['Prüfmittel'] = outputDict['Prüfmittel']
            predictionOutput['Stichprobenverfahren'] = outputDict['Stichprobenverfahren']
            predictionOutput['Lenkungsmethode'] = outputDict['Lenkungsmethode']

            #update stashedTrainData with new rows which don't exist in training data
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

            #get original input file to add output vals into
            originalInputFileSheet = originalInputFile.active
            start_row = 13
            end_row = originalInputFileSheet.max_row  # or set a specific number if needed
            col_pruefmittel = 15
            col_stichprobe = 16
            col_lenkung = 18
            #map lenkungsmethode number value to text value for output
            lm_mapped= []
            mappingFrame = pd.read_excel('data//controlMethod_mappingInfo.xlsx')
            for idx, x in enumerate(outputDict['Lenkungsmethode']):
                lm_mapped.append(mappingFrame.loc[mappingFrame['Lenkungsmethode'] == int(float(outputDict['Lenkungsmethode'][idx])), 'Beschreibung'].item())
            #insert vals into input
            for i, row_num in enumerate(range(start_row, end_row + 1), start=1):
                try:
                    originalInputFileSheet.cell(row=row_num, column=col_pruefmittel).value = outputDict['Prüfmittel'][i-1]
                    originalInputFileSheet.cell(row=row_num, column=col_stichprobe).value = outputDict['Stichprobenverfahren'][i-1]
                    originalInputFileSheet.cell(row=row_num, column=col_lenkung).value = lm_mapped[i-1]
                except:
                    pass

            #initiate download of output
            sio = BytesIO()
            outputName = "output"
            originalInputFile.save(sio)
            sio.seek(0)
            resp = make_response(sio.getvalue())
            resp.headers["Content-Disposition"] = "attachment; filename={}.xlsx".format(outputName)
            resp.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return resp
        return

Function: convertPredDataToDataframe
----------------

Purpose
^^^^^^^^^^^^^^^^
The initial input as desired by Jopp is distinctly formatted and thus not suitable for pre-processing. This function extracts relevant data from the initial input into a dataframe.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): Raw dataframe used as input by Jopp

Process
^^^^^^^^^^^^^^^^
1. Relevant rows and columns are extracted from the input dataframe, and a new dataframe containing raw data suitable for pre-processing is created

Returns
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): Dataframe containing relevant extracted data

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

    def convertPredDataToDataframe(data): #takes the initial input and converts it into a dataframe suitable for predictions
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

        data["Prozesselement"] = prozesselement
        data["Maschine"] = maschine

        return data

Function: createPrediction
----------------

Purpose
^^^^^^^^^^^^^^^^
This function derives the predicted output features for a desired column by employing a pre-trained model on a tuple of input features. Further, a list of predicted probabilities for each classified value is created to provide decision support during the human validation step.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`model` : The model to be used for predictions
- :varname:`predData` (dataframe): The set of raw input data, containing one or multiple input tuples
- :varname:`outputFeature` (string): The name of the desired output feature
- :varname:`conversionMap` (dictionary): A dictionary that maps each possible unique value within a column to a unique numeric value
- :varname:`scaler` : The scaler created during model training which normalizes each input value to a number between 0 and 1

Process
^^^^^^^^^^^^^^^^
1. Data Pre-Processing:
        - Calls the function :varname:`prepareRawData` which cleans the input data before further processing
        - Applying :varname:`conversionMap` which has been built during model training, each value within the input data is replaced with its corresponding numeric value. If a value does not exist within :varname:`conversionMap`, it is paired with a new unique number and added to the dictionary
        - Input features are scaled to values between 0 and 1 using :varname:`scaler` which has been built during model training
2. Feature Prediction:
    - The pre-trained model is applied to the input data, predicting a set of output features, one per input tuple
    - Resulting output features are re-mapped to non-numeric values using :varname:`conversionMap`
3. Probability List Creation:
    - Using the function :varname:`predict_proba`, a probability distribution for each input feature tuple is created, indicating the probability with which each possible output feature is the correct one for each case
    - The created probability tuple of all output features for each input tuple is sorted by probability

Returns
^^^^^^^^^^^^^^^^
- :varname:`predictions_text` (list): The list of output features, derived from their respective input tuples
- :varname:`probaTuple` (list): A list of lists containing all possible output features for each input tuple, paired with their respective probability in being correct

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

    def createPrediction(model, predData, outputFeature, conversionMap, scaler): 
        predData = prepareRawData(predData) #prepare raw data for predictions

        #replace vals in predData with corresponding vals in conversionMap. If doesn't exist in conversionMap, create a new val
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
        
        predData = scaler.transform(predData) #apply scaler to predData
        preds = model.predict(predData) #predict output features
        
        #re-map output vals to their text versions
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
                    pass
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

Function: getUniqueValues
----------------

Purpose
^^^^^^^^^^^^^^^^
This function extracts all unique values within a dataframe and is used when displaying the prediction results on the web-UI.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`data` (dataframe): Any dataframe

Process
^^^^^^^^^^^^^^^^
1. For each column within the dataframe, all unique values are extracted and appended to a list, which is added to a final dictionary containing all lists.

Returns
^^^^^^^^^^^^^^^^
- :varname:`uniqueVals` (dictionary): A dictionary that contains a list of unique values for each column within the dataframe (key)

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar

.. code-block:: python

    def getUniqueValues(data): #extracts all unique values from a dataframe
        uniqueVals = {}
        for col in outputCols:    
            uniqueList =  data[col].unique()
            uniqueList = [str(r) for r in uniqueList]    
            uniqueVals[col] = uniqueList
        return uniqueVals