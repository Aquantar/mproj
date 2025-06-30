Getting Started
===============

The first step was to decide how we wanted to develop the tool. It quickly became clear that we would build a web-based application. To implement this, we used Flask due to its lightweight structure and flexibility. The setup consists of a few essential files and configurations.

__init__.py
^^^^^^^^^^^^^^^^^

This file initializes the Flask application and serves as the entry point for importing core configurations and modules

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)


main.py
^^^^^^^^^^^^

This script is responsible for launching the application and starting the server.

.. code-block:: python

    from app import app

    if __name__ == "__main__":
        print("Starting Flask application...")
        app.run(host="0.0.0.0", port=5000, debug=True)


routes.py
^^^^^^^^^^^^

This file contains the route definitions that link frontend requests to backend logic. Each route corresponds to a specific URL endpoint and handles user interaction or data processing.

- This exemplary route defines the entry point of the web application. It maps both the root URL (/) and /index to the same function.
- methods=['GET', 'POST'] allows the route to handle both GET requests (e.g., loading the page) and POST requests (e.g., submitting form data).
- :varname:`render_template('index.html')` returns the index.html template, which is then rendered and displayed in the user’s browser.

.. code-block:: python

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

Run the program
^^^^^^^^^^^^^^^^^
1.  Make sure to install all necessary libraries using:

.. code-block:: bash

    pip install -r requirements.txt

2.  Ensure all necessary project files and input data to test the system are present 

3.  Start the Flask server

4.  Username for administration page: 

.. code-block:: text

    admin

5.  Passwort for administration page:

.. code-block:: text

    meinpasswort