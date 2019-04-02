from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import numpy
import time

import server
from token_and_sim import convert_to_Array


def create_training_set_for_clauses(ids, withParagraph):
    t0 = time.time()
    t1 = time.time()
    print("----------Starting Creation of Training set----------")
    model_data = []
    model_classes = []
    for id in ids:
        agb = server.Agb.query.get(id)
        for clause in agb.clauses:
            wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
            arrayWordVector = convert_to_Array(wordVector.vector)
            if withParagraph == True:
                 paragraphVector = server.Vector.query.filter_by(paragraph_id=clause.paragraph_id).filter_by(meanVector=True).first()
                 arrayParagrpahVector = convert_to_Array(paragraphVector.vector)
                 model_data.append(arrayWordVector + arrayParagrpahVector)
            else:
                model_data.append(arrayWordVector)
            model_classes.append(clause.trueState)
        print(time.time() - t0, "seconds for ID", id)
        t0 = time.time()

    print("Einträge pro Zeile", len(model_data[8]))
    print("#AGB:", len(model_data), len(model_classes))
    print("Total Time", time.time() - t1)
    print("----------Ending Creation of Training set----------")
    return [model_data, model_classes]

def create_test_set_for_clauses(id, withParagraph):
    print("----------Starting Creation of Test set----------")
    agb = server.Agb.query.get(id)
    test_data = []

    for clause in agb.clauses:
        wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
        arrayWordVector = convert_to_Array(wordVector.vector)
        if withParagraph == True:
            paragraphVector = server.Vector.query.filter_by(paragraph_id=clause.paragraph_id).filter_by(meanVector=True).first()
            arrayParagrpahVector = convert_to_Array(paragraphVector.vector)
            test_data.append(arrayWordVector + arrayParagrpahVector)
        else:
            test_data.append(arrayWordVector)

    print("TestData Länge:", len(test_data))
    print("----------Ending Creation of Test set----------")
    return test_data

def create_training_set_for_paragraphs(ids):
    print("----------Starting Creation of Training set----------")
    model_data = []
    model_classes = []
    for id in ids:
        agb = server.Agb.query.get(id)
        for paragraph in agb.paragraphs:
            wordVector = server.Vector.query.filter_by(paragraph_id=paragraph.id).filter_by(meanVector=True).first()
            arrayWordVector = convert_to_Array(wordVector.vector)
            model_data.append(arrayWordVector)
            model_classes.append(paragraph.trueState)

    print("Einträge pro Zeile", len(model_data[8]))
    print("#AGB:", len(model_data), len(model_classes))
    return [model_data, model_classes]

def create_test_set_for_paragraphs(id):
    agb = server.Agb.query.get(id)
    test_data = []

    for paragraph in agb.paragraphs:
        wordVector = server.Vector.query.filter_by(paragraph_id=paragraph.id).filter_by(meanVector=True).first()
        arrayWordVector = convert_to_Array(wordVector.vector)
        test_data.append(arrayWordVector)

    print("TestData Länge:", len(test_data))
    return test_data

def general_models(models, training_data, test_data):
    result = []
    for counter, (name, model) in enumerate(models):
        classifier = model
        classifier.fit(training_data[0],training_data[1])

        predictions = classifier.predict(test_data)
        result.append(predictions)

    return result

def find_best_prediction(result):
    best_prediction = []
    most_unique = 0
    max_instances = 100
    best_id = 0

    for counter, prediction in enumerate(result):
        #print (prediction)
        unique = numpy.unique(prediction, return_counts=True)
        if len(unique[0]) > most_unique:
            most_unique = len(unique[0])
            max_instances = max(unique[1])
            best_prediction = prediction
            best_id = counter
        elif len(unique[0]) == most_unique:
            if max(unique[1]) < max_instances:
                max_instances = max(unique[1])
                best_prediction = prediction
                best_id = counter
            #elif max(unique[1]) == max_instances:
                #best_prediction = prediction

    #     print("len",len(unique[0]))
    #     print("max", max(unique[1]))
    #     print("---------------------------")
    # print("---------------------------")
    print("Best:", best_prediction)
    print("len:", len(numpy.unique(best_prediction)))
    print("Best ID", best_id)
    print("---------------------------")
    return best_prediction, best_id

def create_predictions(agbid, best_prediction, para_or_clause):
    agb = server.Agb.query.get(agbid)
    for method_counter, model in enumerate(best_prediction):
        if para_or_clause =="para":
            for counter, paragraph in enumerate(agb.paragraphs):
                new_prediction = server.Prediction(predictedState=int(model[counter]), paragraph_id=paragraph.id, method_id=method_counter + 3, agb_id=agbid)
                server.db.session.add(new_prediction)
                server.db.session.commit()
        elif para_or_clause =="clause":
            for counter, clause in enumerate(agb.clauses):
                new_prediction = server.Prediction(predictedState=int(model[counter]), clause_id=clause.id, method_id=method_counter + 3, agb_id=agbid)
                server.db.session.add(new_prediction)
                server.db.session.commit()

def set_models():
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))

    return models

if __name__ == '__main__':
    #id_to_test = input("Enter ID you want to create predictions for: ")
    t_total= time.time()
    models = set_models()
    best_models =[]
    withParagraph = False
    test_from_id = 96
    again = ""

    # labeled_AGBs_Clauses = server.Agb.query.filter_by(clauseIsLabeled=True).all()
    # clause_ids = list(map(lambda agb: agb.id, labeled_AGBs_Clauses))

    # labeled_AGBs_Paragraphs = server.Agb.query.filter_by(paragraphIsLabeled=True).all()
    # paragraph_ids = list(map(lambda agb: agb.id, labeled_AGBs_Paragraphs))
    while test_from_id < 97 and again == "":
        #paragraph_ids = list(range(1,test_from_id))
        #training_data = create_training_set_for_paragraphs(paragraph_ids)
        clause_ids = list(range(1,test_from_id))
        training_data = create_training_set_for_clauses(clause_ids, withParagraph)

        for id_to_test in range(test_from_id, test_from_id + 4):
            print("current ID:", id_to_test)
            test_data = create_test_set_for_clauses(id_to_test, withParagraph)
            # print("Für Klauseln:", clause_ids)

            #test_data = create_test_set_for_paragraphs(id_to_test)
            #print("Für Paragraphen:", paragraph_ids)
            result = general_models(models, training_data, test_data)
            print("Result Länge", len(result))
            # base_predictions = server.Prediction.query.filter_by(agb_id = id_to_test).filter_by(paragraph_id = None).filter_by(method_id = 1).all()
            # base_ids = list(map(lambda pred: pred.predictedState, base_predictions))
            #
            # result.append(numpy.array(base_ids))
            #best, best_id = find_best_prediction(result)
            #if best_id == 5: best_models.append("CS")
            #else: best_models.append(models[best_id][0])
            create_predictions(id_to_test, result, "clause")
            print("###############################")

        test_from_id = test_from_id + 5
        print("Created Predictions up to:", test_from_id-1)
        print(best_models)
        #again = input("Continue? : ")

    print(best_models)
    print(numpy.unique(best_models, return_counts=True))
    print("Done")
    print("Total Time in sec: ", time.time()-t_total)
    #print("Last ID:",id_to_test )