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
        clause.vector = newVector
        db.session.commit()

def create_SentenceVector_cleanedText(id):
    e = Embedder('..\\142')
    agb = server.Agb.query.get(id)

    sentence = list(map(lambda clause : clause.cleanedText.split(','), agb.clauses))
    result = e.sents2elmo(sentence)
    vectorList = []
    print("Anzahl Sätze", len(result))

    for i, ele in enumerate(result):
        data = np.array(ele)
        average = np.average(data, axis=0)
        vectorList.append(average)

        # print (sentence[i])
        # print("Länge für diesen Satz", len(ele), " : ", len(ele[0]))
        # print ("Satz " + str(i) +": ", ele)
        # print("Average",average, "Länge: ", len(average))

    for counter, clause in enumerate(agb.clauses):
        #print ("Klausel :", clause.rawText)
        newVector = ','.join(str(x) for x in vectorList[counter])
        clause.vector = newVector
        db.session.commit()

if __name__ == '__main__':
    id = input("Enter ID: ")
    task = input("Choose Method: ")
    if task == "raw" : create_SentenceVector_rawText(id)
    elif task == "cle": create_SentenceVector_cleanedText(id)

    print("Code run (hopefully successfully)")
    print ("Your last Input:", id)