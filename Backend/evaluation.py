from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import time

import server
from token_and_sim import convert_to_Array

def set_models():
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))
    models.append(('SVM', SVC(gamma='auto')))
    return models

def get_data(paraOrClause):
    model_data = []
    model_classes = []
    if paraOrClause == "para":
        paraVectors = server.Vector.query.filter_by(clause_id = None).all()
        allParagraphs = server.Paragraph.query.all()
        print ("paraVectors", len(paraVectors))
        print ("allPara", len(allParagraphs))
        data= list(zip(paraVectors, allParagraphs))
        for entry in data:
            arrayWordVector = convert_to_Array(entry[0].vector)
            model_data.append(arrayWordVector)
            model_classes.append(entry[1].trueState)

        print("Model Data", len(model_data))
        print(len(model_data[258]))
        print("Model Classes", len(model_classes))

    elif paraOrClause == "clause":
        clauseVectors = server.Vector.query.filter_by(paragraph_id=None).all()
        allClauses = server.Clause.query.all()
        print ("clauseVector", len(clauseVectors))
        print ("allClauses", len(allClauses))
        data= list(zip(clauseVectors, allClauses))
        for entry in data:
            arrayWordVector = convert_to_Array(entry[0].vector)
            model_data.append(arrayWordVector)
            model_classes.append(entry[1].trueState)

        print("Model Data", len(model_data))
        print(len(model_data[258]))
        print("Model Classes", len(model_classes))

    return [model_data, model_classes]

if __name__ == '__main__':
    poc = input("Enter p OR c: ")
    t0 = time.time()
    models = set_models()
    if poc == "p": data = get_data("para")
    elif poc == "c": data = get_data("clause")

    seed = 7
    scoring = 'accuracy'
    for name, model in models:
        print("-----------In Model", name, "--------------")
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        print("kfold done")
        cv_results = model_selection.cross_val_score(model, data[0], data[1], cv=kfold, scoring=scoring)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)

    print("Final time:", time.time()- t0)
    print("Done")