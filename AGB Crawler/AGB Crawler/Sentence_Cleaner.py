from nltk.tokenize import word_tokenize
import sys
import re
import spacy
from gensim.models.doc2vec import TaggedDocument

reload(sys)
sys.setdefaultencoding('utf-8')
nlp = spacy.load('de')

stopword_list = []
#globalIndex = 1

with open("deutsch_stopwords.txt", 'r') as stopwords:
    for line in stopwords:
        stopword_list.append(line.rstrip())

def prepare_text(filename, whatType):
    testData = []
    #global globalIndex
    with open("Text Extraction/txt_output/cleaned_output/%s" %filename, 'r') as file:
        for idTag, line in enumerate(file):
            # Remove first line, that is empty in all .txt files because all .txt files start with irrelevant symbols
            if idTag == 0:
                continue
            # Removing german-style lower quotation marks
            lowerQM = "\xe2\x80\x9e".encode('utf-8')
            # Removing german-style upper quotation marks
            upperQM ="\xe2\x80\x9c".encode('utf-8')
            # Removing special symbols
            removeTheseChar = "[" + lowerQM + upperQM + '").!,:\';\"/(*?"' + "]"
            cleanedText = re.sub(removeTheseChar, ' ', line)
            cleanedText = re.sub('E-mail', 'email', cleanedText)
            cleanedText = re.sub('-', '', cleanedText)

            # Removing Umlaute
            cleanedText = re.sub('\xc3\xa4'.encode('utf-8'), 'ae', cleanedText)
            cleanedText = re.sub('\xc3\xb6'.encode('utf-8'), 'oe', cleanedText)
            cleanedText = re.sub('\xc3\xbc'.encode('utf-8'), 'ue', cleanedText)
            cleanedText = re.sub('\xc3\x9f'.encode('utf-8'), 'ss', cleanedText)
            cleanedText = re.sub('\xc3\x84'.encode('utf-8'), 'Ae', cleanedText)
            cleanedText = re.sub('\xc3\x96'.encode('utf-8'), 'Oe', cleanedText)
            cleanedText = re.sub('\xc3\x9c'.encode('utf-8'), 'Ue', cleanedText)
            #print "Cleaned Text \n-------------\n", cleanedText
            clause = word_tokenize(cleanedText)
            # convert all words to lowercase
            place = 0
            for word in clause:
                clause[place] = word.lower()
                place += 1
            # Removing all words from my stopword list
            #print "Vorher", clause
            for word in list(clause):
                if word in stopword_list:
                    #print "-----Das Wort***  ", word, "  ***steht auf meiner Liste-----"
                    clause.remove(word)
            #print "Nachher", clause
            if whatType == "doc2vec":
                tagged = TaggedDocument(words=clause, tags=[filename + "_%s" % idTag])
                #globalIndex += 1
                #print tagged
                testData.append(tagged)
            else:
                testData.append(clause)


    #print "Anzahl der Saetze in testData: ", len(testData)
    #del testData[0]
    #print testData
    return testData

#prepare_text("real GmbH.txt", "doc2vec")

