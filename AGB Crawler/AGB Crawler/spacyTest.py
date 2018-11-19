from nltk.tokenize import word_tokenize
import sys
import re
import spacy

reload(sys)
sys.setdefaultencoding('utf-8')

nlp = spacy.load('de')

stopword_list = []

with open("deutsch_stopwords.txt", 'r') as stopwords:
    for line in stopwords:
        stopword_list.append(line.rstrip())

def prepare_text(filename):
    testData = []
    with open("Text Extraction/txt_output/cleaned_output/%s" %filename, 'r') as file:
        for line in file:
            # Removing german-style lower quotation marks
            lowerQM = "\xe2\x80\x9e".encode('utf-8')
            # Removing german-style upper quotation marks
            upperQM ="\xe2\x80\x9c".encode('utf-8')
            # Removing special symbols
            removeTheseChar = "[" + lowerQM + upperQM + '").!,:\';\"/(*"' + "]"
            cleanedText = re.sub(removeTheseChar, ' ', line)
            cleanedText = re.sub('E-mail', 'email', cleanedText)
            cleanedText = re.sub('-', ' ', cleanedText)

            # Removing Umlaute
            cleanedText = re.sub('\xc3\xa4'.encode('utf-8'), 'ae', cleanedText)
            cleanedText = re.sub('\xc3\xb6'.encode('utf-8'), 'oe', cleanedText)
            cleanedText = re.sub('\xc3\xbc'.encode('utf-8'), 'ue', cleanedText)
            cleanedText = re.sub('\xc3\x84'.encode('utf-8'), 'Ae', cleanedText)
            cleanedText = re.sub('\xc3\x96'.encode('utf-8'), 'Oe', cleanedText)
            cleanedText = re.sub('\xc3\x9c'.encode('utf-8'), 'Ue', cleanedText)
            cleanedText = re.sub('\xc3\x9f'.encode('utf-8'), 'ss', cleanedText)
            cleanedText = re.sub('\n', ' ', cleanedText)
            cleanedText = nlp(cleanedText.decode('utf-8'))
            #print "test",cleanedText
            clause = [token.lemma_ for token in cleanedText if not (token.is_stop or token.is_space)]
            # for token in cleanedText:
            #     #print token.lemma_
            #     if token.is_stop == False:
            #         clause.append(token.lemma_)

            #clause = word_tokenize(cleanedText)
            # convert all words to lowercase
            # place = 0
            # for word in clause:
            #     clause[place] = word.lower()
            #     place += 1
            # Removing all words from my stopword list
            # for word in clause:
            #     if str(word) in stopword_list:
            #         clause.remove(word)
            testData.append(clause)


    #print "Anzahl der Saetze in testData: ", len(testData)
    del testData[0]
    print testData
    return testData

prepare_text("real GmbH.txt")
