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

