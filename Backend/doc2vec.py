import server
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

def get_tokenized_data_para():
    docs = []
    labels = []
    for id in range(1,100):
        agb = server.Agb.query.get(id)
        for paragraph in agb.paragraphs:
            token = paragraph.tokenText.split(',')
            docs.append(token)
            labels.append(paragraph.id)

    return list(zip(docs, labels))

def get_tokenized_data_clauses():
    docs = []
    labels = []
    for id in range(1,100):
        agb = server.Agb.query.get(id)
        for clause in agb.clauses:
            token = clause.tokenText.split(',')
            docs.append(token)
            labels.append(clause.id)

    return list(zip(docs, labels))

def build_model(data):
    tagged_data = []
    for i, doc in enumerate(data):
        tagged_data.append(TaggedDocument(words=doc[0], tags=[doc[1]]) )
    print(tagged_data[1])
    print(len(tagged_data))


    model = Doc2Vec(vector_size=256, dm=1)
    model.build_vocab(tagged_data)

    for epoch in range(100):
        model.train(tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.iter)

    ##### Model Name has to be changed for each new Model
    ##### Naming is based on Type (Paragraph or Clause), Vector size and underlying model architecture
    model.save("d2v_c256.model")

if __name__ == '__main__':
    poc = input("Enter 'p' for paragraphs OR 'c' for clauses: ")
    data = []

    if poc == "p": data = get_tokenized_data_para()
    elif poc == "c": data = get_tokenized_data_clauses()


    build_model(data)
    print("Done")



