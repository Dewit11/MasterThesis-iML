import server
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

def get_tokenized_data_para():
    docs = []
    labels = []
    for id in range(1,100):
        #print("------------------", id)
        agb = server.Agb.query.get(id)
        for paragraph in agb.paragraphs:
            token = paragraph.tokenText.split(',')
            docs.append(token)
            labels.append(paragraph.id)
        #print(len(docs), len(labels))

    return list(zip(docs, labels))

def get_tokenized_data_clauses():
    docs = []
    labels = []
    for id in range(1,100):
        #print("------------------", id)
        agb = server.Agb.query.get(id)
        for clause in agb.clauses:
            token = clause.tokenText.split(',')
            docs.append(token)
            labels.append(clause.id)
        #print(len(docs), len(labels))

    return list(zip(docs, labels))

def build_model(data):
    tagged_data = []
    for i, doc in enumerate(data):
        tagged_data.append(TaggedDocument(words=doc[0], tags=[doc[1]]) )
    print(tagged_data[1])
    print(len(tagged_data))

    max_epochs = 100
    vec_size = 256
    alpha = 0.025

    model = Doc2Vec(vector_size=vec_size, alpha=alpha, min_alpha=0.00025, min_count=1, dm=1)
    model.build_vocab(tagged_data)

    for epoch in range(max_epochs):
        print('iteration {0}'.format(epoch))
        model.train(tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.iter)
        # decrease the learning rate
        model.alpha -= 0.0002
        # fix the learning rate, no decay
        model.min_alpha = model.alpha


    print(model.docvecs['Grundwahrheit_6'])
    model.save("d2v_c256.model")

if __name__ == '__main__':
    poc = input("Enter p OR c: ")
    data = []

    if poc == "p": data = get_tokenized_data_para()
    elif poc == "c": data = get_tokenized_data_clauses()

    print(len(data))

    build_model(data)
    print("Done")



