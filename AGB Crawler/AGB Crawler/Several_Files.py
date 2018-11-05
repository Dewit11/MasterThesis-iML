from nltk.tokenize import word_tokenize
import sys
import re

from gensim.models import Word2Vec
import numpy as np
from numpy import dot
from numpy.linalg import norm
import os

reload(sys)
sys.setdefaultencoding('utf-8')

testData = []#
i = 0
print (os.listdir("Text Extraction/txt_output/cleaned_output/"))
for filename in os.listdir("Text Extraction/txt_output/cleaned_output/"):
    if i > 5: break
    with open("Text Extraction/txt_output/cleaned_output/%s" % filename, 'r') as file:
        for line in file:
            # Removing german-style lower quotation marks
            lowerQM = "\xe2\x80\x9e".encode('utf-8')
            # Removing german-style upper quotation marks
            upperQM ="\xe2\x80\x9c".encode('utf-8')
            removeTheseChar = "[" + lowerQM + upperQM + '").!,:\';\"/(*"' + "]"
            cleanedText = re.sub(removeTheseChar, ' ', line)
            #print "Cleaned Text \n-------------\n", cleanedText
            clause = word_tokenize(cleanedText)
            #convert all words to lowercase
            place = 0
            for word in clause:
                clause[place] = word.lower()
                place += 1
            #filtering out Section Titels
            if len(clause) < 4: continue
            testData.append(clause)
        i += 1

print "Anzahl der Saetze in testData: ", len(testData)

model = Word2Vec(testData, min_count=1, size=100)
vocab = model.wv.vocab.keys()
print vocab
wordsInVocab = len(vocab)
print (model.similarity('kunde', 'vertrag'))

def sent_vectorizer(sent, model):
    sent_vec = np.zeros(100)
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

#for entry in results:
#    print (entry)

print "Woerter", vocab
print "# Woerter", wordsInVocab
print "Anzahl der Saetze in testData: ", len(testData)
print "Anzahl der Zeilen in results: ", len(results)
print "Anzahl der Spalten in results: ", len(results[0])

print "Geht lowercase?", testData[1]
print "Ja/Nein", [word.lower() for word in testData[1]]

print model.most_similar('kunde')