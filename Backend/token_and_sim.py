from scipy import spatial
import string
import spacy

import server
#from server import db

#setting classes on our Groundtruth
def set_trueState(id):
    agb = server.Agb.query.get(id)

    for counter, clause in enumerate(agb.clauses):
        clause.trueState = counter
        server.db.session.commit()

def highest_similarity(id, method_id):
    print("----------Cosine Similarity started----------")
    base_agb = server.Agb.query.get(1)
    agb = server.Agb.query.get(id)

    for clause in agb.clauses:

        similarityVector = []
        wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
        # print("To Check", wordVector.clause_id)
        arrayVector = convert_to_Array(wordVector.vector)

        for base_clause in base_agb.clauses:
            base_clause_wordVector = server.Vector.query.filter_by(clause_id = base_clause.id).filter_by(meanVector = True).first()
            #print("Base clause", base_clause_wordVector.clause_id)
            arrayBaseVector = convert_to_Array(base_clause_wordVector.vector)
            similarity = 1 - spatial.distance.cosine(arrayVector, arrayBaseVector)
            similarityVector.append(similarity)
        # print (similarityVector)
        # print("Max: ", max(similarityVector))
        # print ("Index: ", similarityVector.index(max(similarityVector)))
        #clause.basePredictedState = similarityVector.index(max(similarityVector))
        my_prediction = similarityVector.index(max(similarityVector))
        new_prediction = server.Prediction(predictedState=my_prediction, clause_id=clause.id, method_id=method_id, agb_id = id)
        server.db.session.add(new_prediction)
        server.db.session.commit()

    print("----------Cosine Similarity ended----------")


def convert_to_Array(vectorAsString):
    asArray = list(map(float, vectorAsString.split(',')))
    return asArray

def tokenize_clause(id):
    print("----------Tokenization started----------")
    nlp = spacy.load('de')

    agb = server.Agb.query.get(id)
    punctuation = string.punctuation
    numbers = string.digits

    for clause in agb.clauses:
        doc = nlp(clause.rawText)
        vector = []
        for token in doc:
            if (token.is_stop or token.is_space or (token.text in punctuation) or (token.text in numbers)): continue
            vector.append(token.text)
        clause.cleanedText = ','.join(vector)
        server.db.session.commit()

    print("----------Tokenization ended----------")
    return


if __name__ == '__main__':
    id = input("Enter ID: ")
    task = input("Choose Method: ")
    if task =="set" : set_trueState(id)
    elif task =="sim": highest_similarity(id, 1)
    elif task =="tok": tokenize_clause(id)
    # else:
    #     print ("Gibts nicht")
    #     for x in range(1,12):
    #         highest_similarity_rawText(x)

    # clause = server.Clause.query.get("Grundwahrheit_Vorlage_bevh_21")
    # clause.rawText = "(8) Geraten  Sie  mit  einer  Zahlung  in  Verzug,  so  sind  Sie  zur  Zahlung  der gesetzlichen   Verzugszinsen   in   Höhe   von   5   Prozentpunkten   über   dem Basiszinssatz verpflichtet. Für  jedes  Mahnschreiben,  das  nach  Eintritt  des Verzugs an Sie versandt wird, wird Ihnen eine Mahngebühr in Höhe von 2,50EUR   berechnet,   sofern   nicht im   Einzelfall   ein   niedrigerer   bzw.   höherer Schaden nachgewiesen wird."
    # print(clause.rawText)
    # db.session.commit()
    print("Code run (hopefully successfully)")
    print ("Your last Input:", id)

#asString = ','.join(str(x) for x in result[0][0])
#print (asString)

#asArray = list(map(float, asString.split(',')))
#print(asArray)
