from sklearn.metrics import recall_score, f1_score, precision_score
import server
import random

def get_scores_for_classification():
    my_true = []
    my_pred = []
    again = ""
    num = 2
    while num < 100 and again == "":
        for id in range(num, num+5):
            #Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = 1).filter_by(agb_id = id).all()
            #all = server.Paragraph.query.filter_by(agb_id = id).all()
            Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=1).filter_by(agb_id = id).all()
            all = server.Clause.query.filter_by(agb_id = id).all()

            for x in Pred:
                my_pred.append(x.predictedState)
            for y in all:
                my_true.append(y.trueState)

            rand = random.randint(0,len(Pred)-1)
            print(all[rand].id)
            print(Pred[rand].clause_id)


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

if __name__ == '__main__':
    # ids = []
    # preds =[]
    # for id in range (1, 100):
    #     ids.append(id)
    #     Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id=2).filter_by(agb_id=id).all()
    #     preds.append(len(Pred))
    #     #server.db.session.delete(Pred)
    #     #server.db.session.commit()
    #
    # print("ID:", ids)
    # print(preds)
    get_scores_for_classification()
    print("Done")




