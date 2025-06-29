Model Training
================

1: trainNewModel
----------------

Purpose
^^^^^^^^^^^^^^^^
This function fully delegates the training of new predictive model for a single desired output feature, including data preprocessing, model training, and model selection.

Parameters
^^^^^^^^^^^^^^^^
- :varname:`outputFeature` (string): The feature to be predicted based on input data
- :varname:`trainData` (dataframe): The set of raw training data

Process
^^^^^^^^^^^^^^^^
1. Data Pre-Processing:
        - Calls the function :varname:`prepareRawData` which cleans the training data before further processing
        - Create Conversion Map: A map which maps each value of in the training data to a number which is unique within that feature column is created, and the training data is converted to numbers using this map
        - Create Training/Testing Split: The data is split into a training/testing set at an 80/20 ratio, and further is split into input and output features, resulting in :varname:`X_train`, :varname:`X_test`, :varname:`y_train`, :varname:`y_test`
        - Input Feature Scaling: Input features are scaled to values between 0 and 1
2. Model Training:
    - Models of the four selected algorithms are trained with the prepared training data from step 1 using the functions :varname:`randomForest`, :varname:`knn`, :varname:`svm`, and :varname:`neuralNetwork`
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