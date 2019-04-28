from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
import numpy
import time

import server
from token_and_sim import convert_to_Array


def create_training_set_for_clauses(ids):
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
            model_data.append(arrayWordVector)
            model_classes.append(clause.trueState)
        print(time.time() - t0, "seconds for ID", id)
        t0 = time.time()

    print("Einträge pro Zeile", len(model_data[8]))
    print("#AGB:", len(model_data), len(model_classes))
    print("Total Time", time.time() - t1)
    print("----------Ending Creation of Training set----------")
    return [model_data, model_classes]

def create_test_set_for_clauses(id):
    print("----------Starting Creation of Test set----------")
    agb = server.Agb.query.get(id)
    test_data = []

    for clause in agb.clauses:
        wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
        arrayWordVector = convert_to_Array(wordVector.vector)
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

def find_most_unique_prediction(result):
    best_prediction = []
    most_unique = 0
    max_instances = 100

    for counter, prediction in enumerate(result):
        unique = numpy.unique(prediction, return_counts=True)
        if len(unique[0]) > most_unique:
            most_unique = len(unique[0])
            max_instances = max(unique[1])
            best_prediction = prediction
        elif len(unique[0]) == most_unique:
            if max(unique[1]) < max_instances:
                max_instances = max(unique[1])
                best_prediction = prediction

    print("Best:", best_prediction)
    print("len:", len(numpy.unique(best_prediction)))
    print("---------------------------")
    return best_prediction

def create_predictions(agbid, predictions, para_or_clause, method_ids):
    agb = server.Agb.query.get(agbid)
    for method_counter, model in enumerate(predictions):
        if para_or_clause =="para":
            for counter, paragraph in enumerate(agb.paragraphs):
                new_prediction = server.Prediction(predictedState=int(model[counter]), paragraph_id=paragraph.id, method_id=method_ids[method_counter], agb_id=agbid)
                server.db.session.add(new_prediction)
                server.db.session.commit()
        elif para_or_clause =="clause":
            for counter, clause in enumerate(agb.clauses):
                new_prediction = server.Prediction(predictedState=int(model[counter]), clause_id=clause.id, method_id=method_ids[method_counter], agb_id=agbid)
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

def predctions_creation_process(id, for_paragraphs):
    models = set_models()
    ##### Order based on Methods in our database and Models in this code
    method_ids =[3,4,5,6,7,2]
    if for_paragraphs == True:
        labeled_AGBs_Paragraphs = server.Agb.query.filter_by(paragraphIsLabeled=True).all()
        paragraph_ids = list(map(lambda agb: agb.id, labeled_AGBs_Paragraphs))
        test =list(range(5,18))
        training_data = create_training_set_for_paragraphs(test)
        test_data = create_test_set_for_paragraphs(id_to_test)
        ##### Fetch Cosine Similarity Predctions for Most Unique Entries Test
        base_predictions = server.Prediction.query.filter_by(agb_id=id_to_test).filter_by(clause_id=None).filter_by(method_id=1).all()
    else:
        labeled_AGBs_Clauses = server.Agb.query.filter_by(clauseIsLabeled=True).all()
        clause_ids = list(map(lambda agb: agb.id, labeled_AGBs_Clauses))
        training_data = create_training_set_for_clauses(clause_ids)
        test_data = create_test_set_for_clauses(id_to_test)
        ##### Fetch Cosine Similarity Predctions for Most Unique Entries Test
        base_predictions = server.Prediction.query.filter_by(agb_id=id_to_test).filter_by(paragraph_id=None).filter_by(method_id=1).all()

    base_ids = list(map(lambda pred: pred.predictedState, base_predictions))

    result = general_models(models, training_data, test_data)

    dummy_result = result.copy()
    dummy_result.append(numpy.array(base_ids))

    most_unique = find_most_unique_prediction(dummy_result)
    result.append(most_unique)
    if for_paragraphs == True:
        create_predictions(id_to_test, result, "para", method_ids)
    else:
        create_predictions(id_to_test, result, "clause", method_ids)

if __name__ == '__main__':
    id_to_test = input("Enter ID you want to create predictions for: ")
    print("Process for Paragraphs? ")
    ask_for_type = input("Default is 'True', type anything else for 'False': ")
    if ask_for_type =="":
        for_paragraphs = True
    else:
        for_paragraphs = False

    t_total= time.time()
    predctions_creation_process(id_to_test, for_paragraphs)
    print("############### Done ###############")
    print("Total Time in sec: ", time.time()-t_total)
