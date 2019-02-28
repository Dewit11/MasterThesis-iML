from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import numpy

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

def create_training_set(ids, withParagraph):
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

    #print("Zeilen in DatenSet:", len(model_data))
    print("Einträge pro Zeile", len(model_data[8]))
    #print("Klassen", model_classes)
    #print("Zeilen in Klassifizierung", len(model_classes))

    return [model_data, model_classes]

def create_test_set(id, withParagraph):
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

    return test_data


def general_models(models, training_data, test_data):
    for counter, (name, model) in enumerate(models):
        classifier = model
        classifier.fit(training_data[0],training_data[1])

        predictions = classifier.predict(test_data)
        print(counter,") Using ", name, " the Prediction is ", predictions)
        print("Number of entries", len(predictions))
        print("Number of Unique entries:", len(numpy.unique(predictions)))
        print(numpy.unique(predictions))

if __name__ == '__main__':
    withParagraph = False
    models= [('DTC',DecisionTreeClassifier()),('KNN', KNeighborsClassifier()), ('MLP', MLPClassifier()), ('RFC', RandomForestClassifier())]
    training_data = create_training_set([1], withParagraph)
    test_data = create_test_set(8, withParagraph)
    general_models(models, training_data, test_data)



    print("Done")