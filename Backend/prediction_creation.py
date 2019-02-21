from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

import server
from token_and_sim import convert_to_Array

# #{height, weights, shoe size}
# X = [[190,70,44],[166,65,45],[190,90,47],[175,64,39],[171,75,40],[177,80,42],[160,60,38],[144,54,37]]
# Y = ['tu','male','tu','male','female','tu','female','female']
#
# #Predict for this vector (height, wieghts, shoe size)
# P = [[175,70,42]]
#
#
# #{K Neighbors Classifier}
# knn = KNeighborsClassifier()
# knn.fit(X,Y)
# print ("2) Using K Neighbors Classifier Prediction is " + str(knn.predict(P)))

def create_training_set(ids):
    model_data = []
    model_classes = []
    for id in ids:
        agb = server.Agb.query.get(id)
        for clause in agb.clauses:
            wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
            arrayWordVector = convert_to_Array(wordVector.vector)
            paragraphVector = server.Vector.query.filter_by(paragraph_id=clause.paragraph_id).filter_by(meanVector=True).first()
            arrayParagrpahVector = convert_to_Array(paragraphVector.vector)

            model_data.append(arrayWordVector + arrayParagrpahVector)
            model_classes.append(clause.trueState)

    print("Zeilen in DatenSet:", len(model_data))
    print(len(model_data[8]))
    print("Klassen", model_classes)
    print("Zeilen in Klassifizierung", len(model_classes))

    return [model_data, model_classes]

def create_test_set(id):
    agb = server.Agb.query.get(id)
    test_data = []

    for clause in agb.clauses:
        wordVector = server.Vector.query.filter_by(clause_id=clause.id).filter_by(meanVector=True).first()
        arrayWordVector = convert_to_Array(wordVector.vector)
        paragraphVector = server.Vector.query.filter_by(paragraph_id=clause.paragraph_id).filter_by(meanVector=True).first()
        arrayParagrpahVector = convert_to_Array(paragraphVector.vector)

        test_data.append(arrayWordVector + arrayParagrpahVector)

    return test_data


#{Decision Tree Model}
def decision_tree(training_data, test_data):
    clf = DecisionTreeClassifier()
    clf = clf.fit(training_data[0],training_data[1])

    predictions = (clf.predict(test_data))
    print(len(predictions))
    print ("1) Using Decision Tree Prediction is " , predictions)




if __name__ == '__main__':
    training_data = create_training_set([1])
    test_data = create_test_set(6)
    decision_tree(training_data,test_data)

    print("Done")