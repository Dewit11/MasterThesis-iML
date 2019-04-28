import server

def create_Method(name):
    new_Method = server.Method(algorithm=name)

    server.db.session.add(new_Method)
    server.db.session.commit()

def delete_Method(id):
    method = server.Method.query.get(id)

    print("Gelöscht wird: ", method.algorithm)
    server.db.session.delete(method)
    server.db.session.commit()

if __name__ == '__main__':
    #create_Method("True State")
    #delete_Method(2)

    print("Done")
