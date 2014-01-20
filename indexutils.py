__author__ = 'rogersjeffrey'
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import time
from os import listdir

#Creates an instance of the porters stemmer
def porter_stemmer():
     stemmer=PorterStemmer()
     return stemmer
#returns the stemmed word for a given word using porters stemmer
def return_stemmed_word(word):
     stemmed_word= porter_stemmer().stem(word)
     if stemmed_word [ len(stemmed_word)-1] == "'":
        stemmed_word=stemmed_word[:len(stemmed_word)-1]
     return stemmed_word

# returns true if a word is a stop word
def return_is_stop_word(word):
    if word not in stopwords.words('english'):
       return False
    else:
       return True
# tokenizes a string  removing punctuations
# hypehnated words are preserved
def tokenize_string_without_punctuations(input_string):
    tokenizer = RegexpTokenizer(r'(\w+[-]*(\w)*)')
    return tokenizer.tokenize(input_string)
#constructs a path given a directory and file
# eg for input /cranfieldDocs and cranfield001
# it creates /cranfieldDocs/cranfield001

def construct_path(directory,file):

      if directory.endswith("/") or directory.endswith("\\"):
         return directory+file
      else:
         return  directory+"/"+file
#returns all the files in a path
#if path does not exist throws an exception
# if directory is empty it throws an exception
def get_files_in_path(path):
    files=None
    try:
     files= listdir(path)
     if files ==None:
        raise OSError
     return files

    except OSError:
     print "Invalid path.  Kindly enter a valid path to the corpus"
     raise SystemExit
def gettime():
    return time.time()





