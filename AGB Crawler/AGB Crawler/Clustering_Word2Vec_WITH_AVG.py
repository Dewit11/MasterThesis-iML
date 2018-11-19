from nltk.tokenize import word_tokenize
import sys
import re

from gensim.models import Word2Vec
import numpy as np
from numpy import dot
from numpy.linalg import norm
import Sentence_Cleaner as SC
import os

reload(sys)
sys.setdefaultencoding('utf-8')

testData =[]
i = 0

for filename in os.listdir("Text Extraction/txt_output/cleaned_output/"):
    if i > 5: break
    sentences = SC.prepare_text(filename)
    testData.extend(sentences)
    i += 1


#print len(testData)
#for line in testData: print line
dimensionSize = 100
model = Word2Vec(testData, min_count=1, size=dimensionSize)
vocab = model.wv.vocab.keys()

print "Vocabular:", vocab
print "Length of Vocab:", len(vocab)
print (model.similarity('kunde', 'vertrag'))

def sent_vectorizer(sent, model):
    sent_vec = np.zeros(dimensionSize)
    numw = 0
    for w in sent:
        try:
            sent_vec = np.add(sent_vec, model[w])
            numw += 1
        except:
            pass
    return sent_vec / np.sqrt(sent_vec.dot(sent_vec))


V = []
for sentence in testData:
    V.append(sent_vectorizer(sentence, model))

results = [[0 for i in range(len(V))] for j in range(len(V))]

for i in range(len(V) - 1):
    for j in range(i + 1, len(V)):
        results[i][j] = dot(V[i], V[j]) / norm(V[i]) / norm(V[j])

# for entry in results:
#     print (entry)

print "Anzahl der Saetze in testData: ", len(testData)
print "Anzahl der Zeilen in sesults: ", len(results)

print "Vector", model['kunde']
