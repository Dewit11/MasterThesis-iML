from nltk.tokenize import word_tokenize
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

stopword_list = []
testData = []

with open("deutsch_stopwords.txt", 'r') as stopwords:
    for line in stopwords:
        stopword_list.append(line.rstrip())


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
        # Removing all words from my stopword list
        print "Vorher", len(clause)
        for word in clause:
            if word in stopword_list:
                print "-----Das Wort***  ", word, "  ***steht auf meiner Liste-----"
                clause.remove(word)
        print "Nachher", len(clause)
        testData.append(clause)

print "Anzahl der Saetze in testData: ", len(testData)