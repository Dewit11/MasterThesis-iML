import sys
import Sentence_Cleaner as SC
import os
from gensim.models.doc2vec import Doc2Vec

reload(sys)
sys.setdefaultencoding('utf-8')

trainingData =[]
i = 0
for filename in os.listdir("Text Extraction/txt_output/cleaned_output/"):
    if i > 16: break
    sentences = SC.prepare_text(filename, "doc2vec")
    trainingData.extend(sentences)
    i += 1

#for line in trainingData: print line

dimensions = 100
model = Doc2Vec(vector_size=dimensions, alpha=0.025, min_alpha=0.00025, min_count=1, dm=0)
model.build_vocab(trainingData)

for epoch in range(10):
    print ("iteratrion {0}".format(epoch))
    model.train(trainingData, total_examples=model.corpus_count, epochs=model.iter)
    model.alpha -= 0.0002
    model.min_alpha = model.alpha

print trainingData[2].tags
print trainingData[2].words
print model.docvecs["21run GmbH.txt_3"]
print model.docvecs.most_similar("21run GmbH.txt_3")
print len(trainingData)
print model.wv.vocab.keys()


# print vocab
# print len(vocab)
# print len(trainingData)

