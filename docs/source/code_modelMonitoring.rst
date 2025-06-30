Model Management
=====

Function: monitoring
----------------

Purpose
^^^^^^^^^^^^^^^^
This function is part of routes.py and initializes :varname:`monitoring.html` as part of the Web-UI.

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
1. Checks for a validated user, calls for login otherwise
2. Initializes :varname:`monitoring.html`, extracting relevant data for a graph that displays model performance across output features as well as additional metrics for the current model

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`monitoring.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar, Johannes (Corresponding Web-Overlay :varname:`monitoring.html` built by Johannes)

.. code-block:: python
    @app.route('/monitoring', methods=['GET', 'POST'])
    def monitoring():
        if 'user' not in session:
            return redirect(url_for('login'))

        accuracyData = [[], [], []]
        modelIDs = []
        predictionStats = {}

        try:
            #open modelData.xlsx
            modelMetrics = pd.read_excel('models/modelData.xlsx')

            #extract relevant info for all models (graph)
            accuracyData_1 = [float(i) for i in modelMetrics['accuracy_1'].tolist()]
            accuracyData_2 = [float(i) for i in modelMetrics['accuracy_2'].tolist()]
            accuracyData_3 = [float(i) for i in modelMetrics['accuracy_3'].tolist()]
            accuracyData = [accuracyData_1, accuracyData_2, accuracyData_3]

            modelIDs = modelMetrics['modelID'].tolist()

            #extract relevant info for latest model (prediction data)
            last_row = modelMetrics.iloc[-1]
            predictionStats = {
                'totalPredictions': int(last_row['totalPredictions']),
                'predictionChanged': int(last_row['predictionChanged']),
                'predictionChangeRatio': f"{float(last_row['predictionChangeRatio']) * 100:.2f}%"
            }

        except Exception as e:
            print(f"Error when loading model data: {e}")

        return render_template("monitoring.html", accuracyData=accuracyData, modelIDs=modelIDs, predictionStats=predictionStats)


Function: stasheddata
----------------

Purpose
^^^^^^^^^^^^^^^^
This function is part of routes.py and initializes :varname:`stashedData.html` which displays all input tuples that have been used for prediction, but do not exist in the data used to train the current model (Thus can be used for further training)

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
Checks whether :varname:`stashedTrainData.xlsx` contains rows, displays them in the form of a table if yes.

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`stashedData.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar, Johannes (Corresponding Web-Overlay :varname:`stashedData.html` built by Serdar, Johannes)

.. code-block:: python
    @app.route('/stasheddata', methods=['GET', 'POST'])
    def stasheddata(): #load and display stashed data (new training data which has not been incorporated in a model yet)
        file_path = os.path.join("models", "stashedTrainData.xlsx")

        if not os.path.exists(file_path):
            return render_template("stasheddata.html", data=None, error="Datei nicht gefunden", row_count=0)

        try:
            df = pd.read_excel(file_path, header=0, dtype=str)
            if df.empty:
                return render_template("stasheddata.html", data=None, error="Die Datei ist leer", row_count=0)
            df = df.fillna("--")
            row_count = len(df)
            df['Aktion'] = df.index.map(
                lambda i: f'<form action="/delete_row" method="post" style="display:inline;"><input type="hidden" name="row_index" value="{i}"><button type="submit" style="padding: 10px 20px; background-color: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px;">Löschen</button></form>'
            )
            table_html = df.to_html(classes='table table-striped', index=False, escape=False)
            return render_template("stasheddata.html", data=table_html, error=None, row_count=row_count)

        except Exception as e:
            return render_template("stasheddata.html", data=None, error=str(e), row_count=0)

Function: delete_row
----------------

Purpose
^^^^^^^^^^^^^^^^
This function allows for the deletion of an input tuple displayed in :varname:`stasheddata.html`

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
Removes the selected row from :varname:`stashedData.xlsx`, then re-builds :varname:`stasheddata.html`

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`stashedData.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar (Corresponding Web-Overlay :varname:`stashedData.html` built by Serdar, Johannes)

.. code-block:: python
    @app.route('/delete_row', methods=['POST'])
    def delete_row(): #functionality to delete a row in stashed data view
        row_index = int(request.form['row_index'])
        file_path = os.path.join("models", "stashedTrainData.xlsx")

        try:
            df = pd.read_excel(file_path, header=0, dtype=str)
            df = df.drop(index=row_index)
            df.to_excel(file_path, index=False)
            return redirect(url_for('stasheddata'))
        except Exception as e:
            return render_template("stasheddata.html", data=None, error=str(e))

Function: manage_models
----------------

Purpose
^^^^^^^^^^^^^^^^
This function prepares the three most recent models to be displayed in :varname:`manage_models.html`

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
Accesses :varname:`modelData.xlsx` to extract metrics about the most recent three models and relays this data to :varname:`manage_models.html`. Additionally, a button that allows for a non-current model to be restored as the current model is added.

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`manage_models.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar (Corresponding Web-Overlay :varname:`manage_models.html` built by Serdar)

.. code-block:: python
    @app.route('/manage_models', methods=['GET'])
    def manage_models(): #functionality to view current models
        file_path = os.path.join("models", "modelData.xlsx")

        if not os.path.exists(file_path):
            return render_template("manage_models.html", models=None, error="Datei modelData.xlsx nicht gefunden")

        try:
            df = pd.read_excel(file_path, header=0, dtype=str)
            if df.empty:
                return render_template("manage_models.html", models=None, error="Die Datei ist leer")

            #only show the last 3 rows (most recent models)
            df = df.tail(3).reset_index(drop=True)
            #convert accuracy and ratio columns to whole number percentages
            for col in ['accuracy_1', 'accuracy_2', 'accuracy_3', 'predictionChangeRatio']:
                if col in df.columns:
                    df[col] = df[col].astype(float).map(lambda x: f"{round(x * 100)}%")
            #add action buttons to backup models only (not model1)
            df['Aktion'] = df['modelID'].map(lambda model_id: (
                "" if str(model_id) == "1" else
                f'''<form action="/reset_model" method="post" onsubmit="return confirm('Achtung: Diese Aktion kann nicht rückgängig gemacht werden. Fortfahren?');"><input type="hidden" name="model_id" value="{model_id}"><button type="submit" style="padding:6px 15px; background-color:#dc3545; color:white; border:none; border-radius:4px; cursor:pointer;">Wiederherstellen</button></form>'''
            ))
            df.columns = [
                "Modell-ID", "Trainingsdatum", "Genauigkeit Prüfmittel", "Genauigkeit Stichprobenverfahren",
                "Genauigkeit Lenkungsmethode", "Gesamtanzahl Vorhersagen", "Angepasste Vorhersagen",
                "Änderungsquote", "Aktion"
            ]

            #convert to html table
            models_table = df.to_html(classes='table table-striped', index=False, escape=False)
            return render_template("manage_models.html", models=models_table, error=None)

        except Exception as e:
            return render_template("manage_models.html", models=None, error=str(e))

Function: reset_model
----------------

Purpose
^^^^^^^^^^^^^^^^
This function restores a non-current backup model as the current one.

Parameters
^^^^^^^^^^^^^^^^
- request form that contains the ID of the model to be restored.

Process
^^^^^^^^^^^^^^^^
1. Deletes all rows from :varname:`modelData.xlsx` which appear after the selected model ID
2. Compares training data between the model to be restored to and the current model, re-adds all input tuples which have been added afterwards to :varname:`stashedTrainData.xlsx`
3. Replaces the model in folder :varname:`model1` with the selected model

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`manage_models.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Serdar (Corresponding Web-Overlay :varname:`manage_models.html` built by Serdar)

.. code-block:: python
    @app.route('/reset_model', methods=['POST'])
    def reset_model(): #logic to reset a model to a previous version
        model_id = request.form.get('model_id')
        model_name = "model" + str(model_id)
        if model_name not in ['model2', 'model3']:
            return redirect('/manage_models')  #only allow valid backups
        model_data_path = os.path.join("models", "modelData.xlsx")

        df = pd.read_excel(model_data_path, header=0, dtype=str)
        df_reversed = df[::-1].reset_index(drop=True)

        #find row of selected model
        selected_row = df_reversed[df_reversed['modelID'] == model_id]
        if selected_row.empty:
            return redirect('/manage_models')
        row_index = selected_row.index[0]

        #only keep selected model and older ones
        df_new = df_reversed.iloc[:row_index + 1][::-1]

        #mirror change to excel file
        df_new.to_excel(model_data_path, index=False)

        #reset training data to current selected model and add new "unused" rows back to stashedTrainData
        current_model_path = os.path.join("models", "model1", "currentTrainData.xlsx")
        backup_model_path = os.path.join("models", model_name, "currentTrainData.xlsx")
        stash_path = os.path.join("models", "stashedTrainData.xlsx")

        if os.path.exists(current_model_path) and os.path.exists(backup_model_path):
            current_df = pd.read_excel(current_model_path, dtype=str)
            backup_df = pd.read_excel(backup_model_path, dtype=str)

            #get all training data rows which exist in newest model, but not in the model that we have reset to
            diff_df = pd.concat([current_df, backup_df]).drop_duplicates(keep=False)

            #append rows to stashedTrainData
            if not diff_df.empty:
                if os.path.exists(stash_path):
                    existing_stash_df = pd.read_excel(stash_path, dtype=str)
                    updated_stash_df = pd.concat([existing_stash_df, diff_df], ignore_index=True).drop_duplicates()
                else:
                    updated_stash_df = diff_df
                updated_stash_df.to_excel(stash_path, index=False)

        #replace model1 folder contents
        source_dir = os.path.join("models", model_name)
        dest_dir = os.path.join("models", "model1")
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir)

        #clear model2 and model3
        for backup in ['model2', 'model3']:
            backup_path = os.path.join("models", backup)
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                os.makedirs(backup_path)

        return redirect('/manage_models')

Function: login
----------------

Purpose
^^^^^^^^^^^^^^^^
This function implements the login functionality used to check whether a user is authorized to access :varname:`monitoring.html`

Parameters
^^^^^^^^^^^^^^^^
- None

Process
^^^^^^^^^^^^^^^^
1. Displays a form using :varname:`login.html` which requests a user name and password
2. Verifies the username and password by calling :varname:`verify_password`

Notes
^^^^^^^^^^^^^^^^
- Built by: Johannes (Corresponding Web-Overlay :varname:`login.html` built by Johannes)

.. code-block:: python
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if verify_password(username, password):
                session['user'] = username
                return redirect(url_for('monitoring'))
            else:
                flash("Falscher Benutzername oder Passwort. Bitte versuchen Sie es erneut.")
                return redirect(url_for('login'))
        return render_template('login.html')

Function: verify_password
----------------

Purpose
^^^^^^^^^^^^^^^^
This function checks whether the username and passwort with which a user attempts to access :varname:`monitoring.html` is valid

Parameters
^^^^^^^^^^^^^^^^
- :varname:`username` : User Name
- :varname:`password` : Password

Returns
^^^^^^^^^^^^^^^^
- :varname:`username` if valid, None otherwise

Notes
^^^^^^^^^^^^^^^^
- Built by: Johannes (Corresponding Web-Overlay :varname:`login.html` built by Johannes)

.. code-block:: python
    @auth.verify_password
    def verify_password(username, password):
        if username in users and check_password_hash(users.get(username), password):
            return username
        return None

Function: logout
----------------

Purpose
^^^^^^^^^^^^^^^^
This function logs a user out of the system

Parameters
^^^^^^^^^^^^^^^^
- None

Returns
^^^^^^^^^^^^^^^^
- Reroute to :varname:`logout.html`

Notes
^^^^^^^^^^^^^^^^
- Built by: Johannes (Corresponding Web-Overlay :varname:`logout.html` built by Johannes)

.. code-block:: python
    def logout():
        session.pop('user', None)
        return render_template('logout.html')