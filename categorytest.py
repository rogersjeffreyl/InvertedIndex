from nltk.tokenize import RegexpTokenizer
from collections import OrderedDict
def categorize_input_query(input_query):
    query_category=OrderedDict([])
    boolean_phrase_query_start="False"
    phrasal_not_tokenizer = RegexpTokenizer(r'![\"]+[\w+\s*]+[\"]+')
    word_not_tokenizer = RegexpTokenizer(r'!\w+')
    not_queries_set=set(word_not_tokenizer.tokenize(input_query))
    not_queries_set=not_queries_set.union(phrasal_not_tokenizer.tokenize(input_query))
    modified_not_words=[]
    for words in not_queries_set:
        #removing the not words
        modified_not_words.append(words[1:])
    phrase_tokenizer = RegexpTokenizer(r'[\"](\w+\s*)*[\"]')
    phrase_queries_set=set(phrase_tokenizer.tokenize(input_query))
    print "_______"
    print  phrase_queries_set
    phrase_queries_set=phrase_queries_set.difference(set(modified_not_words))
    print phrase_queries_set
    print not_queries_set
categorize_input_query('!HELLO how are you !"BOSS"')  