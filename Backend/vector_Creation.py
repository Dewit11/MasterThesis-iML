from elmoformanylangs import Embedder
import numpy as np

import server
from server import db



def create_SentenceVector_rawText(id):
    e = Embedder('..\\142')
    agb = server.Agb.query.get(id)

    sentence = list(map(lambda clause : [clause.rawText] , agb.clauses))
    result = e.sents2elmo(sentence)
    vectorList = []
    for i, ele in enumerate(result):
        print (sentence[i][0])
        print ("Satz " + str(i) +" : ", ele[0])
        vectorList.append(ele[0])

    for counter, clause in enumerate(agb.clauses):
        #print ("Klausel :", clause.rawText)
        newVector = ','.join(str(x) for x in vectorList[counter])
        clause.meanVector = newVector
        db.session.commit()

def create_meanVector_cleanedText(id):
    e = Embedder('..\\142')
    agb = server.Agb.query.get(id)

    sentence = list(map(lambda clause : clause.cleanedText.split(','), agb.clauses))
    result = e.sents2elmo(sentence)
    vectorList = []
    print("Anzahl Sätze in sentence", len(sentence))
    print("Anzahl Sätze in result", len(result))

    #create meanVector here
    for counter, wordVectors in enumerate(result):
        data = np.array(wordVectors)
        average = np.average(data, axis=0)
        vectorList.append(average)

        # print (sentence[counter])
        # print("Länge für diesen Satz", len(wordVectors), " : ", len(wordVectors[0]))
        # print ("Satz " + str(counter) +": ", wordVectors)
        # print("Average",average, "Länge: ", len(average))

    for counter, clause in enumerate(agb.clauses):
        #print ("Klausel :", clause.rawText)
        meanVector = ','.join(str(x) for x in vectorList[counter])
        new_meanVector = server.Vector(vector=meanVector, clause_id=clause.id, meanVector=True)
        db.session.add(new_meanVector)
        db.session.commit()
        for vector in result[counter]:
            str_Vector = ','.join(str(x) for x in vector)
            new_vector = server.Vector(vector=str_Vector, clause_id=clause.id, meanVector=False)
            db.session.add(new_vector)
            db.session.commit()
    #


if __name__ == '__main__':
    id = input("Enter ID: ")
    task = input("Choose Method: ")
    if task == "raw" : create_SentenceVector_rawText(id)
    elif task == "cle": create_meanVector_cleanedText(id)

    print("Code run (hopefully successfully)")
    print ("Your last Input:", id)