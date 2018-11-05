from nltk.tokenize import word_tokenize
import sys
import re
import Sentence_Cleaner as SC
import os

from gensim.models import Word2Vec

reload(sys)
sys.setdefaultencoding('utf-8')

trainingData =[]
i = 0
for filename in os.listdir("Text Extraction/txt_output/cleaned_output/"):
    if i > 5: break
    sentences = SC.prepare_text(filename)
    trainingData.extend(sentences)
    i += 1

