from nltk.tokenize import word_tokenize
import sys
import re

from gensim.models import Word2Vec
import numpy as np
from numpy import dot
from numpy.linalg import norm

reload(sys)
sys.setdefaultencoding('utf-8')

testData = []

with open("Text Extraction/txt_output/cleaned_output/real GmbH.txt", 'r') as file:
    for line in file:
        # Removing german-style lower quotation marks
        lowerQM = "\xe2\x80\x9e".encode('utf-8')
        # Removing german-style upper quotation marks
        upperQM ="\xe2\x80\x9c".encode('utf-8')
        removeTheseChar = "[" + lowerQM + upperQM + '").!,:\';\"/(*"' + "]"
        cleanedText = re.sub(removeTheseChar, ' ', line)
        #print "Cleaned Text \n-------------\n", cleanedText
        clause = word_tokenize(cleanedText)
        # convert all words to lowercase
        place = 0
        for word in clause:
            clause[place] = word.lower()
            place += 1
        #if len(clause) < 3: continue
        testData.append(clause)

#print len(testData)
#for line in testData: print line
dimensionSize = 100
model = Word2Vec(testData, min_count=1, size=dimensionSize)
vocab = model.wv.vocab.keys()

print "Vocabular:", vocab
print "Length of Vocab:", len(vocab)
print (model.similarity('im', 'vertrag'))

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

print model['kunde']
