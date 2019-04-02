from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn import model_selection
from gensim.models.doc2vec import Doc2Vec
import time
from multiprocessing import Pool

import server
from token_and_sim import convert_to_Array

def set_models():
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))
    #models.append(('SVM', SVC(gamma='auto')))
    #models.append(('RFC', RandomForestClassifier()))
    return models

def get_data(paraOrClause, with_Doc2Vec):
    model_data = []
    model_classes = []

    if paraOrClause == "para":
        d2v_model = Doc2Vec.load("d2v_p512.model")
        paraVectors = server.Vector.query.filter_by(clause_id = None).all()
        allParagraphs = server.Paragraph.query.all()
        print ("paraVectors", len(paraVectors))
        print ("allPara", len(allParagraphs))
        data= list(zip(paraVectors, allParagraphs))
        for entry in data:
            arrayWordVector = []
            #arrayWordVector = convert_to_Array(entry[0].vector)
            if with_Doc2Vec == True:
                arrayWordVector.extend(d2v_model.docvecs[entry[1].id])
            model_data.append(arrayWordVector)
            model_classes.append(entry[1].trueState)

        print("Model Data", len(model_data))
        print(len(model_data[258]))
        print("Model Classes", len(model_classes))

    elif paraOrClause == "clause":
        d2v_model = Doc2Vec.load("d2v_c512_dm0.model")
        clauseVectors = server.Vector.query.filter_by(paragraph_id=None).all()
        allClauses = server.Clause.query.all()
        print ("clauseVector", len(clauseVectors))
        print ("allClauses", len(allClauses))
        data= list(zip(clauseVectors, allClauses))
        for entry in data:
            arrayWordVector = []
            #arrayWordVector = convert_to_Array(entry[0].vector)
            if with_Doc2Vec == True:
                arrayWordVector.extend(d2v_model.docvecs[entry[1].id])
            model_data.append(arrayWordVector)
            model_classes.append(entry[1].trueState)

        print("Model Data", len(model_data))
        print(len(model_data[258]))
        print("Model Classes", len(model_classes))

    return [model_data, model_classes]

def create_cross_validation(models, data):
    seed = 7
    scoring = []
    #scoring.append('accuracy')
    scoring.append('precision_weighted')
    scoring.append('recall_weighted')
    scoring.append('f1_weighted')
    result=[]
    for name, model in models:
        print("-----------In Model", name, "--------------")
        t0 = time.time()
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        for score in scoring:
            cv_results = model_selection.cross_val_score(model, data[0], data[1], cv=kfold, scoring=score)
            msg = "%s: %f (%f) for %s" % (name, cv_results.mean(), cv_results.std(), score)
            print(msg)
            result.append(cv_results.mean())
        result.append(time.time()-t0)
    return result

if __name__ == '__main__':
    poc = input("Enter p OR c: ")
    t0 = time.time()
    models = set_models()
    data = []
    if poc == "p": data = get_data("para", True)
    elif poc == "c": data = get_data("clause", True)

    pool = Pool()
    result1 = pool.apply_async(create_cross_validation, [models[0:1], data])
    result2 = pool.apply_async(create_cross_validation, [models[1:2], data])
    result3 = pool.apply_async(create_cross_validation, [models[2:3], data])
    result4 = pool.apply_async(create_cross_validation, [models[3:4], data])
    result5 = pool.apply_async(create_cross_validation, [models[4:5], data])
    # result6 = pool.apply_async(create_cross_validation, [models[5:6], data])
    # result7 = pool.apply_async(create_cross_validation, [models[6:7], data])
    answer1 = result1.get(timeout=5000)
    answer2 = result2.get(timeout=5000)
    answer3 = result3.get(timeout=5000)
    answer4 = result4.get(timeout=5000)
    answer5 = result5.get(timeout=5000)
    # answer6 = result6.get(timeout=5000)
    # answer7 = result7.get(timeout=5000), answer7

    answers = [answer1,answer2,answer3,answer4,answer5]
    for i, answer in enumerate(answers):
        print(models[i][0])
        for ele in answer:
            print(ele)


    print("Final time:", time.time()- t0)
    print("Done")