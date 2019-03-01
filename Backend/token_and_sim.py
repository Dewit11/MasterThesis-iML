from scipy import spatial
import string
import spacy

import server
#from server import db

#setting classes on our Groundtruth
def set_trueState(id):
    agb = server.Agb.query.get(id)

    for counter, clause in enumerate(agb.paragraphs):
        clause.trueState = counter
        server.db.session.commit()

    agb.paragraphIsLabeled = True
    server.db.session.commit()

def highest_similarity_clauses(id, method_id):
    print("----------Cosine Similarity for Clauses started----------")
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

        my_prediction = similarityVector.index(max(similarityVector))
        new_prediction = server.Prediction(predictedState=my_prediction, clause_id=clause.id, method_id=method_id, agb_id = id)
        server.db.session.add(new_prediction)
        server.db.session.commit()

    print("----------Cosine Similarity for Clauses ended----------")

def highest_similarity_paragraphs(id, method_id):
    print("----------Cosine Similarity for Paragraphs started----------")
    base_agb = server.Agb.query.get(1)
    agb = server.Agb.query.get(id)

    for paragraph in agb.paragraphs:
        similarityVector = []
        wordVector = server.Vector.query.filter_by(paragraph_id=paragraph.id).filter_by(meanVector=True).first()
        # print("To Check", wordVector.paragraph_id)
        arrayVector = convert_to_Array(wordVector.vector)

        for base_paragraph in base_agb.paragraphs:
            base_paragraph_wordVector = server.Vector.query.filter_by(paragraph_id = base_paragraph.id).filter_by(meanVector = True).first()
            #print("Base clause", base_paragraph_wordVector.paragraph_id)
            arrayBaseVector = convert_to_Array(base_paragraph_wordVector.vector)
            similarity = 1 - spatial.distance.cosine(arrayVector, arrayBaseVector)
            similarityVector.append(similarity)

        my_prediction = similarityVector.index(max(similarityVector))
        new_prediction = server.Prediction(predictedState=my_prediction, paragraph_id=paragraph.id, method_id=method_id, agb_id = id)
        server.db.session.add(new_prediction)
        server.db.session.commit()

    print("----------Cosine Similarity for Paragraphs ended----------")

def convert_to_Array(vectorAsString):
    asArray = list(map(float, vectorAsString.split(',')))
    return asArray

def tokenize_text(id):
    print("----------Tokenization started----------")
    nlp = spacy.load('de')

    agb = server.Agb.query.get(id)
    punctuation = string.punctuation
    numbers = string.digits

    # Checking if we're currently working on clauses (True) or paragraphs(False)
    flag_forClauses = True
    create_token_for = [agb.clauses, agb.paragraphs]

    for clauses_or_parapgraphs in create_token_for:
        print("----------Tokenization for", flag_forClauses, " startet----------")
        for c_OR_p in clauses_or_parapgraphs:
            if flag_forClauses == True:
                doc = nlp(c_OR_p.rawText)
            elif flag_forClauses == False:
                doc = nlp(c_OR_p.title)
            vector = []
            for token in doc:
                if (token.is_stop or token.is_space or (token.text in punctuation) or (token.text in numbers)): continue
                vector.append(token.text)
                c_OR_p.tokenText = ','.join(vector)
            server.db.session.commit()

        print("----------Tokenization for",flag_forClauses," ended----------")
        flag_forClauses = False
    return


if __name__ == '__main__':
    id = input("Enter ID: ")
    task = input("Choose Method: ")
    if task =="set" : set_trueState(id)
    elif task =="sim": highest_similarity_clauses(id, 1)
    elif task =="tok": tokenize_text(id)

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
