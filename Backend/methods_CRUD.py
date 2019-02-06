import server
from server import db

def create_Method(name):
    new_Method = server.Method(algorithm=name)

    db.session.add(new_Method)
    db.session.commit()

def delete_Method(id):
    method = server.Method.query.get(id)

    print("Gelöscht wird: ", method.algorithm)
    db.session.delete(method)
    db.session.commit()

if __name__ == '__main__':
    #create_Method("Some classification")
    delete_Method(2)
    print("Done")
