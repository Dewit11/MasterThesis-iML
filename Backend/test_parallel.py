from sklearn.metrics import recall_score, f1_score, precision_score
import server
import random

def get_scores_for_classification():

    again = ""
    num = 96
    while num < 97 and again == "":
        my_true = []
        my_pred = []
        for id in range(num, num+4):
            #Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = 2).filter_by(agb_id = id).all()
            #all = server.Paragraph.query.filter_by(agb_id = id).all()
            Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=2).filter_by(agb_id = id).all()
            all = server.Clause.query.filter_by(agb_id = id).all()

            for x in Pred:
                my_pred.append(x.predictedState)
            for y in all:
                my_true.append(y.trueState)

            rand = random.randint(0,len(Pred)-1)
            print(all[rand].id)
            print(Pred[rand].paragraph_id)


        print(len(my_pred))
        print(len(my_true))

        pre = precision_score(my_true, my_pred, average='weighted')
        rec = recall_score(my_true, my_pred, average='weighted')
        f1 = f1_score(my_true, my_pred, average='weighted')
        print("Precision",pre)
        print("Recall", rec)
        print("f1",f1)
        print(pre)
        print(rec)
        print(f1)

        print("Entries in Traing Data", num - 1)
        num = num + 5
        again = input("Continue? : ")

def get_best_score():
    num = 6
    method_ids =[1,2,3,4,5,6,7]
    best_for_every_step =[]
    full_predictions = [[], [], [], [], [], [], []]
    while num < 95:
        predictions = []
        my_true = []
        for id in range(num, num + 4):
            #all = server.Paragraph.query.filter_by(agb_id=id).all()
            all = server.Clause.query.filter_by(agb_id=id).all()
            for y in all:
                my_true.append(y.trueState)
        for met_id in method_ids:
            my_pred = []
            for id in range(num, num + 4):
                #Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = met_id).filter_by(agb_id = id).all()
                Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=met_id).filter_by(agb_id=id).all()
                for x in Pred:
                    my_pred.append(x.predictedState)
            pre = precision_score(my_true, my_pred, average='weighted')
            predictions.append(pre)
            full_predictions[met_id-1].append(pre)

        print("Based on", num-1)
        print(predictions)
        print("MAX:", max(predictions))
        print("Position:", predictions.index(max(predictions)))
        best_for_every_step.append(max(predictions))
        num = num + 5
    for ele in full_predictions:
        print("##############################")
        for x in ele:
            print(x)
    print("########################")
    for ele in best_for_every_step: print (ele)
    print (len(best_for_every_step))
if __name__ == '__main__':
    #get_scores_for_classification()
    #get_best_score()
    all = server.Clause.query.all()
    pall = server.Paragraph.query.all()
    print (len(all))
    print (len(pall))
    print("Done")




