from sklearn.metrics import recall_score, f1_score, precision_score
import server

def get_scores_for_classification(for_paragraphs, chosen_Method):
    start_from_id = 6
    step_size = 5

    while start_from_id < 99:
        my_true = []
        my_pred = []
        for id in range(start_from_id, start_from_id+4):
            if for_paragraphs == True:
                Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = chosen_Method).filter_by(agb_id = id).all()
                all = server.Paragraph.query.filter_by(agb_id = id).all()
            else:
                Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id = chosen_Method).filter_by(agb_id = id).all()
                all = server.Clause.query.filter_by(agb_id = id).all()

            for x in Pred:
                my_pred.append(x.predictedState)
            for y in all:
                my_true.append(y.trueState)

        ##### Number of AGBs in Training_Set
        print("##############################")
        print("Based on", start_from_id - 1, "AGBs in Training Set:")

        ##### Evaluation Measures for choosen Method
        pre = precision_score(my_true, my_pred, average='weighted')
        rec = recall_score(my_true, my_pred, average='weighted')
        f1 = f1_score(my_true, my_pred, average='weighted')
        print("Precision : ",pre)
        print("Recall    : ", rec)
        print("f1        : ",f1)

        if start_from_id > 95:
            step_size = 4
        start_from_id = start_from_id + step_size

def get_best_score(for_paragraphs):
    start_from_id = 6
    step_size = 5
    method_ids =[1,2,3,4,5,6,7]
    best_for_every_step =[]
    full_predictions = [[], [], [], [], [], [], []]
    while start_from_id < 99:
        predictions = []
        my_true = []
        for id in range(start_from_id, start_from_id + step_size):
            if for_paragraphs == True:
                all = server.Paragraph.query.filter_by(agb_id=id).all()
            else:
                all = server.Clause.query.filter_by(agb_id=id).all()
            for y in all:
                my_true.append(y.trueState)
        for met_id in method_ids:
            my_pred = []
            for id in range(start_from_id, start_from_id + step_size):
                if for_paragraphs == True:
                    Pred = server.Prediction.query.filter_by(clause_id=None).filter_by(method_id = met_id).filter_by(agb_id = id).all()
                else:
                    Pred = server.Prediction.query.filter_by(paragraph_id=None).filter_by(method_id=met_id).filter_by(agb_id=id).all()
                for x in Pred:
                    my_pred.append(x.predictedState)
            ##### Switch precision_score with f1 or recall, if needed
            pre = precision_score(my_true, my_pred, average='weighted')
            predictions.append(pre)
            full_predictions[met_id-1].append(pre)

        ##### Number of AGBs in Training_Set
        print("Based on", start_from_id-1, "AGBs in Training Set")
        ##### Evaluation Measure of all Methods fot this Step
        print(predictions)
        ##### Best Value and Index of best Value
        print("MAX:", max(predictions))
        print("Position:", predictions.index(max(predictions)))

        best_for_every_step.append(max(predictions))
        ##### Update starting ID for next Step
        if start_from_id > 95:
            step_size = 4
        start_from_id = start_from_id + step_size

    ##### Print Results in steps of 5 for each of our Methods
    ##### (For easy copy and paste to Excel)
    for ele in full_predictions:
        print("##############################")
        for x in ele:
            print(x)

    ##### Print Best Method for each Step
    ##### (For easy copy and paste to Excel)
    print("################### Best Values for each step of size 5 ###################")
    print("### (Starting from ID 6, because the first 5 don't have any predictions) ###")
    for ele in best_for_every_step: print (ele)

if __name__ == '__main__':
    ##### True, if we want to evaluate Paragraphs, False for Clause Evaluation
    for_paragraphs = True
    ##### Choose, which Method all three scores should be calculated for
    chosen_Method = 2

    get_scores_for_classification(for_paragraphs, chosen_Method)
    get_best_score(for_paragraphs)
    print("############### Done ###############")





