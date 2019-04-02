from sklearn.metrics import recall_score, f1_score, precision_score
import server
import random

def get_scores_for_classification():
    my_true = []
    my_pred = []
    again = ""
    num = 6
    while num < 96 and again == "":
        for id in range(num, num+5):
            Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = 3).filter_by(agb_id = id).all()
            all = server.Paragraph.query.filter_by(agb_id = id).all()
            #Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=3).filter_by(agb_id = id).all()
            # all = server.Clause.query.filter_by(agb_id = id).all()

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

def get_best_score(up_to_id):
    num = 6
    while num < up_to_id:
        best_pre = []
        my_true = []
        for id in range(num, num + 5):
            #all = server.Paragraph.query.filter_by(agb_id=id).all()
            all = server.Clause.query.filter_by(agb_id=id).all()
            for y in all:
                my_true.append(y.trueState)
        for met_id in range(3, 8):
            my_pred = []
            for id in range(num, num + 5):
                #Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = met_id).filter_by(agb_id = id).all()
                Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=3).filter_by(agb_id=id).all()
                for x in Pred:
                    my_pred.append(x.predictedState)

            pre = precision_score(my_true, my_pred, average='weighted')
            best_pre.append(pre)

        print(best_pre)
        print("MAX:", max(best_pre))
        num = num + 5
if __name__ == '__main__':
    #get_scores_for_classification()
    get_best_score(95)
    print("Done")




