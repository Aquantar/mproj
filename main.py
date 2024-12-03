import classifier

def main():
    #name des classifiers und spalte, die vorhergesagt werden soll
    #Valide Classifier: 'rf', 'svm', 'knn', 'naiveBayes', 'neuralNetwork'
    #Valide Vorhersagespalten: 'Text zum Fertigungshilfsmittel', 'Stichprobenverfahren', 'Lenkungsmethode', 'Merkmalsgewichtung'
    results = classifier.classifyData('svm', 'Text zum Fertigungshilfsmittel')
    print(results)
    return

if __name__ == '__main__':
  main()
