from nltk.tokenize import word_tokenize
import sys
import re

from gensim.models import Word2Vec
from sklearn import cluster
from sklearn import metrics

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
        if len(clause) < 3: continue
        testData.append(clause)


dimensionSize = 100
model = Word2Vec(testData, min_count=1, size=dimensionSize)
vocab = model[model.wv.vocab.keys()]
wordsInVocab = len(vocab)

kmeans = cluster.KMeans(n_clusters=10)
kmeans.fit(vocab)

labels = kmeans.labels_
centroids = kmeans.cluster_centers_

print ("Cluster id labels for inputted data")
print (labels)
print ("Centroids data")
print (centroids)

print ("Score (Opposite of the value of X on the K-means objective which is Sum of distances of samples to their closest cluster center):")
print (kmeans.score(vocab))

silhouette_score = metrics.silhouette_score(vocab, labels, metric='euclidean')

print ("Silhouette_score: ")
print (silhouette_score)


print "Vocab", vocab
print wordsInVocab
print (model.similarity('im', 'vertrag'))

print "Anzahl der Saetze in testData: ", len(testData)

print model['kunde']
