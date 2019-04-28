from elmoformanylangs import Embedder
import numpy as np
import time

import server

def create_meanVector_cleanedText(id):
    print("----------Vector Creation started----------")

    e = Embedder('..\\142')
    agb = server.Agb.query.get(id)

    ##### To create Vectors while loading the Embedder only once
    create_vectors_for = [agb.clauses, agb.paragraphs]
    ##### Checking if we're currently working on clauses (True) or paragraphs(False)
    flag_forClauses = True

    for clause_or_paragraph in create_vectors_for:
        print("----------Vector Creation for", flag_forClauses, " started----------")
        sentence = list(map(lambda clause : clause.tokenText.split(','), clause_or_paragraph))
        result = e.sents2elmo(sentence)
        vectorList = []
        print("Anzahl Sätze in sentence", len(sentence))
        print("Anzahl Sätze in result", len(result))

        ##### Create meanVector here
        for counter, wordVectors in enumerate(result):
            data = np.array(wordVectors)
            average = np.average(data, axis=0)
            vectorList.append(average)

        for counter, c_OR_p in enumerate(clause_or_paragraph):

            meanVector = ','.join(str(x) for x in vectorList[counter])
            if flag_forClauses == False:
                new_meanVector = server.Vector(vector=meanVector, paragraph_id=c_OR_p.id, meanVector=True)
                server.db.session.add(new_meanVector)
                server.db.session.commit()
            else:
                new_meanVector = server.Vector(vector=meanVector, clause_id=c_OR_p.id, meanVector=True)
                server.db.session.add(new_meanVector)
                server.db.session.commit()

                ##### Uncomment the following code, if all Word Vectors should be stored on its own
                ##### (Not Recommended due to extremly long loading times later on)
                # for vector in result[counter]:
                #     str_Vector = ','.join(str(x) for x in vector)
                #     new_vector = server.Vector(vector=str_Vector, clause_id=c_OR_p.id, meanVector=False)
                #     server.db.session.add(new_vector)
                #     server.db.session.commit()

        print("----------Vector Creation for", flag_forClauses, "ended----------")
        flag_forClauses = False

if __name__ == '__main__':
    id = input("Enter ID: ")
    t0 = time.time()

    create_meanVector_cleanedText(id)

    print("Final time:", time.time() - t0)
