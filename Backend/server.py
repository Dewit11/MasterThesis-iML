from flask import Flask, render_template, jsonify, abort, Response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

import token_and_sim
import vector_Creation

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'FinalDatabaseAGB.sqlite')
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Agb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    isLabeled = db.Column(db.Boolean)


class Paragraph(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)

    agb_id = db.Column(db.Integer, db.ForeignKey('agb.id'))
    agb = db.relationship('Agb', backref='paragraphs')


class Clause(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    rawText = db.Column(db.String)
    cleanedText = db.Column(db.String)
    meanVector = db.Column(db.String)
    basePredictedState = db.Column(db.Integer)
    trueState = db.Column(db.Integer)

    # reference to the original AGB
    agb_id = db.Column(db.Integer, db.ForeignKey('agb.id'))
    agb = db.relationship('Agb', backref='clauses')

    # reference to paragraph within that AGB
    paragraph_id = db.Column(db.String, db.ForeignKey('paragraph.id'))
    paragraph = db.relationship('Paragraph', backref='clauses')


class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String)
    parameter = db.Column(db.String)
    datum = db.Column(db.String)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    predictedState = db.Column(db.Integer)
    trueState = db.Column(db.Integer)
    otherInformation = db.Column(db.String)

    # reference to the original AGB
    agb_id = db.Column(db.Integer, db.ForeignKey('agb.id'))
    agb = db.relationship('Agb', backref='predictions')

    # reference to clause the prediction is made for
    clause_id = db.Column(db.String(255), db.ForeignKey('clause.id'))
    clause = db.relationship('Clause', backref='predictions')

    # reference to the Method used for this prediction
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'))
    method = db.relationship('Method', backref='predictions')

class Vector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String)
    vector = db.Column(db.String)
    meanVector = db.Column(db.Boolean)

    # reference to the original AGB
    agb_id = db.Column(db.Integer, db.ForeignKey('agb.id'))
    agb = db.relationship('Agb', backref='vectors')

    # reference to clause the prediction is made for
    clause_id = db.Column(db.String(255), db.ForeignKey('clause.id'))
    clause = db.relationship('Clause', backref='vectors')


class AgbSchema(ma.ModelSchema):
    class Meta:
        model = Agb

class ParagraphSchema(ma.ModelSchema):
    class Meta:
        model = Paragraph

class ClauseSchema(ma.ModelSchema):
    class Meta:
        model = Clause

class MethodSchema(ma.ModelSchema):
    class Meta:
        model = Method

class PredictionSchema(ma.ModelSchema):
    class Meta:
        model = Prediction

class VectorSchema(ma.ModelSchema):
     class Meta:
         model = Vector


agb_schema = AgbSchema()
agbs_schema = AgbSchema(many=True)

paragraph_schema = ParagraphSchema()
paragraphs_schema = ParagraphSchema(many=True)

clause_schema = ClauseSchema()
clauses_schema = ClauseSchema(many=True)

method_schema = MethodSchema()
methods_schema = MethodSchema(many=True)

prediction_schema = PredictionSchema()
predictions_schema = PredictionSchema(many=True)

vector_schema = VectorSchema()
vectors_schema = VectorSchema(many=True)



# type conversion, since arrays aren't valid data types in out database
def stringToArray(vectorAsString):
    asArray = list(map(int, vectorAsString.split(',')))
    return asArray
def arrayToString(vectorAsArray):
    if isinstance(vectorAsArray, list):
        asString = ','.join(str(x) for x in vectorAsArray)
        return asString
    else: return vectorAsArray

# endpoint to create new AGB
@app.route("/newAGB", methods=["POST"])
def add_agb():
    name = request.json['name']
    clauses = request.json['splitText']
    new_agb = Agb(name = name, isLabeled=False)

    db.session.add(new_agb)
    #db.session.flush()
    db.session.commit()
    for counter, clause in enumerate(clauses):
        print ('Zeile', counter)
        if clause[0]+clause[1]+clause[2] == "---":
            new_ParagraphID = name + "_" + str(counter)
            new_paragraph = Paragraph(id= new_ParagraphID, title = clause[3:], agb_id = new_agb.id)
            db.session.add(new_paragraph)
            #db.session.flush()
            db.session.commit()
        else:
            new_ClauseID = name + "_" + str(counter)
            new_clause = Clause(id= new_ClauseID, rawText = clause, agb_id= new_agb.id, paragraph_id = new_paragraph.id)
            db.session.add(new_clause)


    db.session.commit()
    print ('ID der neuen AGB', new_agb.id)
    print ("Liste der Paragraphen in AGB ", new_agb.paragraphs[0].title)
    print ("Liste der Klauseln in AGB ", new_agb.clauses[0].rawText)
    print ("Anzahl Klauseln", len(new_agb.clauses))
    print ("Anzahl Paragraphen", len(new_agb.paragraphs))

    token_and_sim.tokenize_clause(new_agb.id)
    vector_Creation.create_meanVector_cleanedText(new_agb.id)
    token_and_sim.highest_similarity(new_agb.id, 1)

    return agb_schema.jsonify(new_agb)

@app.route("/addParagraph", methods=["POST"])
def add_paragraph():
    id = request.json['id']
    title = request.json['title']
    agb_id = request.json['agb_id']

    new_paragraph = Paragraph(id = id, title=title, agb_id = agb_id)

    db.session.add(new_paragraph)
    db.session.commit()

    return paragraphs_schema.jsonify(new_paragraph)

@app.route("/addClause", methods=["POST"])
def add_clause():
    id = request.json['id']
    rawText = request.json['rawText']
    agb_id = request.json['agb_id']
    paragraph_id = request.json['paragraph_id']

    new_clause = Clause(id = id, rawText=rawText, agb_id = agb_id, paragraph_id = paragraph_id)

    db.session.add(new_clause)
    db.session.commit()

    return "Klappt"

# endpoint to show all companies
@app.route("/agb", methods=["GET"])
def get_agb():
    all_agbs = Agb.query.all()
    result = agbs_schema.dump(all_agbs)
    return jsonify(result)

# endpoint to show all methods
@app.route("/methods", methods=["GET"])
def get_methods():
    all_methods = Method.query.all()
    result = methods_schema.dump(all_methods)
    return jsonify(result)

@app.route("/allMeanVectors/", methods=["GET"])
def all_Mean_Vectors():
    all_vectors = Vector.query.filter_by(meanVector = True)
    return vectors_schema.jsonify(all_vectors)

@app.route("/allPredictions/", methods=["GET"])
def get_predictions():
    all_predictions = Prediction.query.all()
    result = predictions_schema.dump(all_predictions)
    return jsonify(result)

@app.route("/predictions/<int:method_id>", methods=["GET"])
def get_prediction(method_id):
    all_predictions = Prediction.query.filter_by(method_id=method_id)
    return predictions_schema.jsonify(all_predictions)

@app.route("/predictions/<int:agb_id>/<int:method_id>", methods=["GET"])
def get_prediction_forAGB(agb_id, method_id):
    all_predictions = Prediction.query.filter_by(method_id=method_id).filter_by(agb_id=agb_id )
    return predictions_schema.jsonify(all_predictions)

# endpoint to get agb detail by id
@app.route("/agb/<int:id>", methods=["GET"])
def agb_detail(id):
    agb = Agb.query.get(id)
    return agb_schema.jsonify(agb)

@app.route("/paragraph/<string:id>", methods=["GET"])
def paragraph_detail(id):
    paragraph = Paragraph.query.get(id)
    return paragraph_schema.jsonify(paragraph)

@app.route("/paragraphsFromAGB/<int:id>", methods=["GET"])
def allParagraphsInAGB(id):
    all_paragraphs = Paragraph.query.filter_by(agb_id = id)
    return paragraphs_schema.jsonify(all_paragraphs)

@app.route("/clausesFromParagraph/<string:id>", methods=["GET"])
def allClausesInParagraph(id):
    all_clauses = Clause.query.filter_by(paragraph_id = id)
    return clauses_schema.jsonify(all_clauses)

@app.route("/clausesFromAGB/<int:id>", methods=["GET"])
def allClausesInAGB(id):
    all_clauses = Clause.query.filter_by(agb_id = id)
    return clauses_schema.jsonify(all_clauses)

@app.route("/clausesByClass/<int:agbID>/<int:classID>", methods=["GET"])
def ClausesInClass(agbID, classID):
    all_clauses = Clause.query.filter_by(agb_id = agbID).filter_by(basePredictedState = classID)
    return clauses_schema.jsonify(all_clauses)

# endpoint to update company
# @app.route("/company/<int:id>", methods=["PUT"])
# def user_update(id):
#     company = Company.query.get(id)
#     name = request.json['name']
#     fullText = arrayToString(request.json['splitText'])
#
#     company.name = name
#     company.fullText = fullText
#
#     db.session.commit()
#     return company_schema.jsonify(company)


# endpoint to delete company
@app.route("/agb/<int:id>", methods=["DELETE"])
def user_delete(id):
    agb = Agb.query.get(id)
    Paragraph.query.filter_by(agb_id=id).delete()
    Clause.query.filter_by(agb_id=id).delete()
    Vector.query.filter_by(agb_id=id).delete()
    Prediction.query.filter_by(agb_id=id).delete()
    db.session.delete(agb)
    db.session.commit()

    return agb_schema.jsonify(agb)



if __name__ == '__main__':
    app.run(debug=True)
    # print 'test', Agb.query.all()
    # print 'und was anderes', Agb.query.filter_by(title='Hallo').first()
