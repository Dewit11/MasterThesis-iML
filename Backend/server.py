from flask import Flask, render_template, jsonify, abort, Response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import numpy
import token_and_sim
import vector_Creation

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'FinalDatabaseAGB_V4.sqlite')
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Agb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    clauseIsLabeled = db.Column(db.Boolean)
    paragraphIsLabeled = db.Column(db.Boolean)


class Paragraph(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    tokenText = db.Column(db.String)
    trueState = db.Column(db.Integer)

    agb_id = db.Column(db.Integer, db.ForeignKey('agb.id'))
    agb = db.relationship('Agb', backref='paragraphs')


class Clause(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    rawText = db.Column(db.String)
    tokenText = db.Column(db.String)
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

    # reference to paragraph the prediction is made for
    paragraph_id = db.Column(db.String, db.ForeignKey('paragraph.id'))
    paragraph = db.relationship('Paragraph', backref='predictions')

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

    # reference to paragraph the prediction is made for
    paragraph_id = db.Column(db.String, db.ForeignKey('paragraph.id'))
    paragraph = db.relationship('Paragraph', backref='vectors')

    # reference to clause the vector is made for
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
    new_agb = Agb(name = name, clauseIsLabeled=False, paragraphIsLabeled=False)

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

    token_and_sim.tokenize_text(new_agb.id)
    # vector_Creation.create_meanVector_cleanedText(new_agb.id)
    # token_and_sim.highest_similarity_paragraphs(new_agb.id, 1)
    # token_and_sim.highest_similarity_clauses(new_agb.id, 1)

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

@app.route("/setTrueState/<string:type>", methods=["PUT"])
def set_trueState(type):
    classes = request.json['classes']
    agbid = request.json['agbid']
    print("AGBid", agbid)

    for counter, entries in enumerate(classes):
        #print("Klasse ", counter,":", entries)
        for item in entries:
            #print("Klausel:",counter, item['id'])
            if type == "clause":
                entry = Clause.query.get(item['id'])
            elif type == "paragraph":
                entry = Paragraph.query.get(item['id'])
            entry.trueState = counter
            db.session.commit()

    agb = Agb.query.get(agbid)
    print("AGB", agb.name)
    if type == "clause": agb.clauseIsLabeled = True
    if type == "paragraph": agb.paragraphIsLabeled = True
    db.session.commit()
    return paragraphs_schema.jsonify(classes)

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
    all_agbs = Agb.query.with_entities(Agb.id, Agb.name, Agb.clauseIsLabeled, Agb.paragraphIsLabeled).all()
    result = agbs_schema.dump(all_agbs)
    return jsonify(result)

# endpoint to show all methods
@app.route("/methods", methods=["GET"])
def get_methods():
    all_methods = Method.query.with_entities(Method.id, Method.algorithm).all()
    result = methods_schema.dump(all_methods)
    return jsonify(result)

@app.route("/allMeanVectors/", methods=["GET"])
def all_Mean_Vectors():
    all_vectors = Vector.query.filter_by(meanVector = True)
    print(all_vectors.count())
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

@app.route("/predictions/<string:type>/<int:agb_id>/<int:method_id>", methods=["GET"])
def get_prediction_forAGB(type, agb_id, method_id):
    if type == "paragraph":
        all_predictions = Prediction.query.filter_by(method_id=method_id).filter_by(agb_id=agb_id).filter_by(clause_id = None)
    elif type == "clause":
        all_predictions = Prediction.query.filter_by(method_id=method_id).filter_by(agb_id=agb_id).filter_by(paragraph_id = None)
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
    all_paragraphs = Paragraph.query.with_entities(Paragraph.id, Paragraph.title, Paragraph.trueState).filter_by(agb_id = id)
    #all_paragraphs = Paragraph.query.filter_by(agb_id = id)
    return paragraphs_schema.jsonify(all_paragraphs)

@app.route("/paragraphsFromClause/<string:id>", methods=["GET"])
def paragraphForClause(id):
    clause = Clause.query.get(id)
    searchFor = clause.paragraph_id
    print(searchFor)
    paragraph = Paragraph.query.get(searchFor)
    #.with_entities(Paragraph.id, Paragraph.title, Paragraph.trueState)
    my_para= Paragraph.query.with_entities(Paragraph.id, Paragraph.title, Paragraph.trueState).filter_by(id = searchFor).first()
    print(paragraph)
    print(my_para)
    return paragraph_schema.jsonify(my_para)

@app.route("/clausesFromParagraph/<string:id>", methods=["GET"])
def allClausesInParagraph(id):
    all_clauses = Clause.query.filter_by(paragraph_id = id)
    return clauses_schema.jsonify(all_clauses)

@app.route("/clausesFromAGB/<int:id>", methods=["GET"])
def allClausesInAGB(id):
    all_clauses = Clause.query.with_entities(Clause.id, Clause.rawText, Clause.trueState).filter_by(agb_id = id)
    #all_clauses = Clause.query.filter_by(agb_id = id)
    return clauses_schema.jsonify(all_clauses)

@app.route("/dataFromClass/<string:poc>/<int:classID>", methods=["GET"])
def clausesFromClass(poc, classID):
    if poc =="clause":
        all_clauses = Clause.query.with_entities(Clause.id, Clause.rawText, Clause.trueState).filter_by(trueState = classID)
        return clauses_schema.jsonify(all_clauses)
    elif poc == "paragraph":
        all_paragraphs = Paragraph.query.with_entities(Paragraph.id, Paragraph.title, Paragraph.trueState).filter_by(trueState = classID)
        return paragraphs_schema.jsonify(all_paragraphs)


@app.route("/data/<string:whatData>", methods=["GET"])
def getData(whatData):
    agb = Agb.query.get(1)
    result = []
    other_classes = [5,10,12,21,24,29,37,40,45,48,51,55]
    if whatData == "clauses":
        for counter, clause in enumerate(agb.clauses):
            all_clauses = Clause.query.filter_by(trueState = counter).all()
            if counter in other_classes:
                new_class = {"x": counter, "y": len(all_clauses), "color": "red"}
            else:
                new_class = {"x": counter, "y": len(all_clauses)}
            result.append(new_class)
    elif whatData == "uniqueClauses":
        for counter, clause in enumerate(agb.clauses):
            clauses_in_class_x = Clause.query.filter_by(trueState = counter).all()
            clause_ids = list(map(lambda my_clause: my_clause.agb_id, clauses_in_class_x))
            unique = numpy.unique(clause_ids)
            if counter in other_classes:
                new_class = {"x": counter, "y": len(unique), "color": "red"}
            else:
                new_class = {"x": counter, "y": len(unique)}
            result.append(new_class)
    elif whatData == "paragraphs":
        for counter, paragraph in enumerate(agb.paragraphs):
            all_paragraphs = Paragraph.query.filter_by(trueState = counter).all()
            if counter == 12:
                new_class = {"x": counter, "y": len(all_paragraphs), "color": "red"}
            else:
                new_class = {"x": counter, "y": len(all_paragraphs)}
            result.append(new_class)
    elif whatData == "uniqueParagraphs":
        for counter, paragraph in enumerate(agb.paragraphs):
            paragraphs_in_class_x = Paragraph.query.filter_by(trueState = counter).all()
            paragraph_ids = list(map(lambda my_paragraph: my_paragraph.agb_id, paragraphs_in_class_x))
            unique = numpy.unique(paragraph_ids)
            if counter == 12:
                new_class = {"x": counter, "y": len(unique), "color": "red"}
            else:
                new_class = {"x": counter, "y": len(unique)}
            result.append(new_class)
    return jsonify(result)


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

