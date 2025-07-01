Conclusion
=====

The developed system demonstrated a strong predictive performance, achieving an average accuracy of approximately 86% across the three core output features—validation equipment (~92.5%), sampling rate (~80%), and validation procedure (~85%). These results underline the model’s capability to support the creation of control plans in a reliable and data-driven manner.

Overall, the implementation of this predictive system led to significant improvements in the control plan creation process. Most notably, it drastically reduced the time required to develop such plans and minimized the risk of human error. Additionally, it lowered the need for human resources in the decision-making phase and as a result increased the standardization of the process. Thanks to its data-driven architecture, the system also enables continuous self-improvement through ongoing re-training with new data—ensuring it remains robust and relevant in future use cases.


Deployment
^^^^^^^^^^^^^^^^^

The goal is to deploy the application within the Jopp infrastructure and make it usable for them.
We used a containerized approach with Docker. This allows for simple deployment on any target system without the need to install dependencies manually.

Dockerfile
^^^^^^^^^^^^^^^^^

The project is containerized using the following Dockerfile.

.. code-block:: python

    # Basis-Image auswählen
    FROM python:3.9

    # Arbeitsverzeichnis im Container setzen
    WORKDIR /app

    # Abhängigkeiten kopieren und installieren
    COPY requirements.txt requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Alle Projektdaten kopieren
    COPY . .

    # Port freigeben
    EXPOSE 5000

    # Startbefehl für die Anwendung
    CMD ["python", "main.py"]

Requirements
^^^^^^^^^^^^^^^^^

All necessary Python libraries are defined in the requirements.txt file.

.. code-block:: python
    
    Flask==3.1.0
    pandas==2.2.3
    scikit_learn==1.6.1
    xlsxwriter==3.1.9
    gunicorn==21.2.0
    openpyxl==3.1.2
    Flask-HTTPAuth

Deployment Steps
^^^^^^^^^^^^^^^^^

1. **Build the Docker image locally:**

   .. code-block:: bash

      docker build -t flask-app .

2. **Test the image locally:**

   .. code-block:: bash

      docker run -p 5000:5000 flask-app

3. **Export the image as a `.tar` file:**

   .. code-block:: bash

      docker save flask-app > flask-app.tar

4. **Transfer the image to the test PC via SCP:**

   The test PC is accessible via SSH on port ``5522``. Use the following command:

   .. code-block:: bash

      scp -P 5522 /path/to/flask-app.tar serdar_isik@212.185.51.181:/home/serdar_isik/

   Alternatively:

   .. code-block:: bash

      scp -P 5522 /path/to/flask-app.tar johannes_klauer@212.185.51.181:/home/johannes_klauer/

   SSH credentials:

   - **User:** serdar_isik  
     **Password:** FyElT*********

   - **User:** johannes_klauer  
     **Password:** NXZj*********

5. **SSH into the remote machine (via Windows Terminal, Bash, or similar):**

   .. code-block:: bash

      ssh serdar_isik@212.185.51.181 -p 5522

6. **Load the image on the test PC:**

   .. code-block:: bash

      docker load < flask-app.tar

7. **Run the container on the test PC and map to port 80:**

   .. code-block:: bash

      docker run -d -p 80:5000 flask-app

8. **Access the web application:**

   The container exposes port 5000 internally, which is mapped to port 80 on the host.
   The application is reachable under:

   .. code-block:: text

      http://212.185.51.181:5580


Notes
^^^^^^^^^^^^^^^^^
Deployment done by Johannes