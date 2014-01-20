__author__ = 'rogersjeffrey'
import cPickle as pickle
from collections import OrderedDict
from nltk.tokenize import RegexpTokenizer
from nltk.metrics import distance  as distance
import indexutils
import result_formatter
import re
import math
import string
import time
from xml.dom import minidom
import copy
class QueryProcessor:
    query_type_tuple=("PHRASE","NOT","AND","WORD")

    def __init__(self):
        self.query_cache={}
        self.index_instance={}
        self.doc_index_instance={}
        self.phrase_index_instance={}
        self.group_iteration=0
        self.grouping_iteration=0
        self.time_taken_to_query=0
        self.query_array_length=0
        self.index_copy={}

    # Replace the punctuations in  the string
    def replace_punctuation_in_query_string(self,query_string):
        punctuation=string.punctuation
        punctuation=punctuation.replace("-","")
        punctuation=punctuation.replace("!","")
        punctuation=punctuation.replace('"',"")
        table = string.maketrans("","")
        return_query_string=query_string.translate(table,punctuation)
        return return_query_string

    def categorize_input_query(self,input_query):
        query_category=OrderedDict([])

        input_query=self.replace_punctuation_in_query_string(input_query)
        phrasal_not_tokenizer = RegexpTokenizer(r'![\"]+(\w+[-]*(\w+)*(\s*)(\w)*)*[\"]')
        word_not_tokenizer = RegexpTokenizer(r'!(\w+[-]*(\w)*)')

        not_queries_set=set(word_not_tokenizer.tokenize(input_query))
        not_queries_set=not_queries_set.union(set(phrasal_not_tokenizer.tokenize(input_query)))
        string_copy=input_query
        string_copy = re.sub(r"\".*?\"", "", string_copy)
        string_copy = re.sub(r"!.*?(\s|$)", "", string_copy)

        modified_not_words=[]
        for words in not_queries_set:
            #removing the not words
            modified_not_words.append(words[1:])
        phrase_tokenizer = RegexpTokenizer(r'[\"]+(\w+[-]*(\w+)*(\s*)(\w)*)*[\"]')
        phrase_queries_set=set(phrase_tokenizer.tokenize(input_query))

        phrase_queries_set=phrase_queries_set.difference(set(modified_not_words))
        query_category["PHRASE"]=phrase_queries_set
        query_category["NOT"]=modified_not_words
        normal_words=string_copy.split()
        normal_word_set=set(normal_words )
        query_category["WORD"]=normal_word_set
        return query_category

    def is_a_phrase_query(self,word):
        if word[0]=='"':
            return True
        else:
            return False

    def process_query_removing_special_characters(self,word):
        return indexutils.tokenize_string_without_punctuations(word)


    # processes the input phrase query removing all the quotes and stopwords and does stemming as well
    # this method pre processes the input query  removing special chars like  ,-,_,*,.,),[
    def process_input_phrase_query(self,phrase):
        phrasal_word=self.process_query_removing_special_characters(phrase)
        new_sentence=""
        for word in  phrasal_word:

               if indexutils.return_is_stop_word(word)==False:
                 current_word=indexutils.return_stemmed_word(word)
                 new_sentence=new_sentence+" "+current_word
        return new_sentence.strip()

    # Processes all the queries and returns the appropriate result of the query
    def get_results_of_input_query_as_per_category(self,input_query_type_collection):
        not_query_results=OrderedDict([])
        phrase_query_results=OrderedDict([])
        normal_query_results=OrderedDict([])
        final_query_results=OrderedDict([])

        for query_type in input_query_type_collection:
            if query_type == QueryProcessor.query_type_tuple[1]:
                #NOT QUERY TYPE
                query_list=input_query_type_collection[query_type]
                for query in query_list:
                    if self.is_a_phrase_query(query):
                       new_phrasal_query=self.process_input_phrase_query(query)
                       not_query_results[query]=self.return_phrase_query_result(new_phrasal_query)
                    else:
                        not_query_results[query]=self.return_query_results(self.process_input_phrase_query(query))

            elif query_type == QueryProcessor.query_type_tuple[0]:
                #Phrase Query processing
                query_list=input_query_type_collection[query_type]
                for query in query_list:
                     new_sentence=self.process_input_phrase_query (query)
                     phrase_query_results[query]=self.return_phrase_query_result(new_sentence)

            elif query_type == QueryProcessor.query_type_tuple[3]:
                # Normal Words

                query_list=input_query_type_collection[query_type]
                for query in query_list:
                    normal_query_results[query]=self.return_query_results(self.process_input_phrase_query(query))
        final_query_results["NOT"]=  not_query_results
        final_query_results["WORD"]=normal_query_results
        final_query_results["PHRASE"]=phrase_query_results

    # Returns the result of  a single word
    # Basically lists the documents and the tfs the word occurs in
        return final_query_results
    def return_query_results(self,word):

        if(self.index_instance.has_key(word)):

           query_result=self.index_copy[word]
           return query_result
        else:
          return None

    #This method computes the  result of a not query
    # if documents D1 D2 D3 match a query the documents other that D1,D2,D3 are returned
    def return_not_query_result(self,documents):

        if documents==None:
            return set(self.doc_index_instance)
        else:
            return set(self.doc_index_instance).difference(documents)

    def edit_distance(self,input_word,hash_word):

        return distance.edit_distance(input_word,hash_word)

    # Computes the  edit distance between words and returns words with edit distance1
    def process_similar_query(self,input_word):
        result_set=[]
        for key in set(self.index_instance.keys()):

                hash_word=key
                edit_distance=self.edit_distance(input_word,hash_word)
                if edit_distance==1:

                   result_set.append(key)

        return result_set
    def return_document_text(self,document_id):
        documentText="Document Not found"
        try:
            doc_path=self.doc_index_instance[document_id]["path"]
            documentContent=minidom.parse(doc_path)
            documentText=str(documentContent.getElementsByTagName('TEXT')[0].firstChild.data.strip())
        except KeyError:
            documentText="Document Not found"
        return documentText
    def return_document_title(self,document_id):
        document_title="Document Not found"
        try:
          document_title=self.doc_index_instance[document_id]["title"]

        except KeyError:
           document_title="Document Not found"
        return  document_title
    def process_query(self,input_query):
        self.grouping_iteration=0 #setting this flag every time the qyery processing starts
        # TODO implement query caching

        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

        start_time=time.time()
        self.index_copy=copy.deepcopy(self.index_instance.copy())
        end_time=time.time()
        query=input_query.strip().split(" ",1)
        query_command=query[0]
        #sself.reload_index_file()

        if  query_command=="doc":
            query_command_value=query[1]
            self.return_document_text(query_command_value)
            end_time=time.time()
            self.time_taken_to_query=end_time-start_time

        elif query_command=="title":
             query_command_value=query[1]
             title=self.return_document_title(query_command_value)
             print HEADER+title+ENDC
             end_time=time.time()
             self.time_taken_to_query=end_time-start_time

        elif query_command=="similar":
             query_command_value=query[1]
             if query_command_value==None:
                print WARNING+"Please enter  the word for which you have to find similar words"+ENDC
             else:

                 word_list=self.process_query_removing_special_characters(query_command_value)
                 final_result=[]
                 for word in word_list:
                     result=self.process_similar_query(word)
                     final_result=final_result+result

                 if len(final_result)==0:
                    print FAIL+"No similar words found with edit distance of 1"+ENDC
                 else:
                    for match_word in final_result:
                        print match_word
             end_time=time.time()
             self.time_taken_to_query=end_time-start_time
        elif query_command=="df":
            query_command_value=""
            try:
              query_command_value=query[1]
            except IndexError:
                print FAIL+"Please enter the word whose document frequency is to be found"+ENDC


            if  query_command_value:

                if indexutils.return_is_stop_word(query_command_value):
                   print 0
                   print WARNING+"The word given is a stop word. Stop words are not indexed"+ENDC
                else:

                   query_category=self.categorize_input_query(query_command_value)
                   query_results=self.get_results_of_input_query_as_per_category(query_category)
                   final_result=self.aggregate_query_results(query_results)
                   end_time=time.time()
                   self.time_taken_to_query=end_time-start_time
                   if final_result:
                      print len(final_result)
                   else:
                      print 0
            else:
                print WARNING+"Enter a word or a phrases"+ENDC

        elif query_command=="tf":
            query=input_query.split()
            document_id=""

            term=""
            try:
              document_id=query[1]
              term=query[2]
            except IndexError:
                print FAIL+"Please enter the document and word whose term frequency is to be found"+ENDC

            if indexutils.return_is_stop_word(term):
                   print 0
                   print WARNING+"The word given is a stop word"+ENDC
            elif self.doc_index_instance.has_key(document_id):
              if self.index_instance.has_key(term):
                 if self.index_instance[term].has_key(document_id):
                    print self.index_instance[term][document_id][0]
                 else:
                     print 0
                     print FAIL+"Word not present in document "+document_id+ENDC
            else:
                 print FAIL+"Document "+document_id+ " not found"+ENDC
            end_time=time.time()
            self.time_taken_to_query=end_time-start_time
        elif query_command=="freq":
            try:
              query_command_value=query[1]
              term=query_command_value
              query_category=self.categorize_input_query(term)
              query_results=self.get_results_of_input_query_as_per_category(query_category)
              final_result=self.aggregate_query_results(query_results)
              no_of_times=0

              if final_result:
                 for results in query_results:
                     for phrasal_queries in query_results[results]:

                         length=len(phrasal_queries)
                         for document in query_results[results][phrasal_queries]:

                              no_of_times=no_of_times+int( query_results[results][phrasal_queries][document][0])


                 print (no_of_times/self.query_array_length)
              else:
                 print FAIL+"No matching documents found for phrase "+OKGREEN+term+ENDC

            except IndexError:
                print FAIL+"Please enter the phrase whose frequency is to be found"+ENDC

            end_time=time.time()
            self.time_taken_to_query=end_time-start_time
        else:
            query_category=self.categorize_input_query(input_query)
            query_results=self.get_results_of_input_query_as_per_category(query_category)
            final_result=self.aggregate_query_results(query_results)
            end_time=time.time()
            self.time_taken_to_query=end_time-start_time
            if final_result:
               print self.print_final_results(final_result,query_results)
               print "\n"
            else:
               print FAIL+"No matching Results Found"+ENDC

        print "time taken to  search: %f seconds" %self.time_taken_to_query

    def aggregate_query_results(self,query_results):
        # substitute the phrase count for single doc

        final_result={}

        for query_type in query_results:
            queries_and_results=query_results[query_type]


            for queries in queries_and_results:
                result={}
                result=queries_and_results[queries]
                if query_type==QueryProcessor.query_type_tuple[1]:
                   complimentary_not_query_result={}
                   not_query_actual_result_docs=self.return_not_query_result(queries_and_results[queries])

                   for document in not_query_actual_result_docs:
                      complimentary_not_query_result.update({document:[1]})
                   result=complimentary_not_query_result

                if result:
                    for document in result:
                           if final_result.has_key(document):
                              current_count=int(final_result[document])
                              current_count=current_count+int(result[document][0])
                              final_result[document]=current_count
                           else:

                              final_result.update({document:result[document][0]})
        return (final_result)
#"laminar-floor" "protuberances permissible on laminar-flow surfaces at"
    def print_final_results(self,final_result,query_results):


        OKGREEN = '\033[92m'
        ENDC = '\033[0m'
        item_count=0
        exit_flag=0
        for item in sorted(final_result.items()):

            item_count=item_count+1
            print "\n"
            print OKGREEN+item[0]+" : "+str(item[1])+ENDC
            result_formatter.print_query_snippet(self.doc_index_instance[item[0]]["path"],query_results)
            if(item_count%3==0):
                while (True):
                    query=raw_input('Displayed %d results out of %d.\n Press Enter to continue "x" or "X" to start a new search' %(item_count,(len(final_result))))
                    if query=='':
                       break
                    if query=='X' or query=='x':
                        exit_flag=1
                        break
            if exit_flag==1:
               break


    def reload_index_file(self):

         self.index_instance=pickle.load( open("index.p","rb"))
         self.doc_index_instance=pickle.load( open("documentindex.p","rb"))


    def construct_phrase_groups(self,phrase_word_list):


        if phrase_word_list==None or phrase_word_list==[]:
           return None

        self.grouping_iteration=self.grouping_iteration+1
        if self.grouping_iteration==1:
            phrase_word_list=phrase_word_list[::-1]
        bi_phrase_groups={}
        is_a_group_phrase=0
        phrasal_word_count=len(phrase_word_list)
        grp=""
        if phrase_word_list[0] =="<grp>":
           self.group_iteration=self.group_iteration+1

           phrase_word_list=phrase_word_list[1:]

           phrasal_word_count=phrasal_word_count-1
        number_of_bi_phrase_groups=(phrasal_word_count%2)+phrasal_word_count/2
        phrasal_group_count=0
        for i in range(0,phrasal_word_count):
            if (i+1)%2==0:
                phrasal_group_count= phrasal_group_count+1
                bi_phrase_groups.update({str(phrasal_group_count):[phrase_word_list[i-1],phrase_word_list[i]]})
        if phrasal_group_count < number_of_bi_phrase_groups:
           bi_phrase_groups.update({str(phrasal_group_count+1):[phrase_word_list[phrasal_word_count-1]]})

        return bi_phrase_groups

    def return_phrase_query_result(self,query):
        self.phrase_index_instance={}

        result={}
        result=self.process_phrase_in_query(query)

        length=len(query.strip().split())

        self.query_array_length=length

        if result:
            for each_document in result:


                result[each_document][0]=result[each_document][0]*len(query.strip().split())


            return result
        else:
            return None


    def process_phrase_in_query(self,phrase):

        phrase_word_list=[]
        phrase_word_list=phrase.split()
        processed_word_list=[]

        phrase_group=None
        new_set=None

        phrase_group=self.construct_phrase_groups(phrase_word_list)

        if phrase_group==None or phrase_group==[]:
            return None
        group_counter=0
        prev_phrase_group_document_list={}
        prev_phrase_group_document_set=""
        prev_phrase_group_documents={}
        # setting it to null because this has to contain entries for only the new groupings formed

        self.phrase_index_instance={}
        for group in sorted(phrase_group.keys()):
            relevant_doc_for_phrase={}
            group_counter=group_counter+1
            current_group=phrase_group[group]

            relevant_doc_for_phrase=self.process_phrase_group(group,current_group,1)


            if relevant_doc_for_phrase:
                if relevant_doc_for_phrase[str(group_counter)]:
                   self.phrase_index_instance.update(relevant_doc_for_phrase)
                else:
                   return None
            else:
                return None
            if(group_counter>1):


                  new_set=set(relevant_doc_for_phrase[group]).intersection(prev_phrase_group_document_set)
                  prev_phrase_group_document_list=new_set
                  try:
                    new_set.pop()

                    prev_phrase_group_document_set=set(relevant_doc_for_phrase[group]).intersection(prev_phrase_group_document_set)

                    new_documents_list={}


                    for key in prev_phrase_group_document_set:


                        current_group_result_length=len(relevant_doc_for_phrase[group][key])
                        previous_group_result_length=len(self.phrase_index_instance[str(group_counter-1)][key])

                        for  length_1 in range(1,current_group_result_length ):
                              for length_2  in range(1,previous_group_result_length):


                                   if self.phrase_index_instance[str(group_counter-1)][key][length_2]-relevant_doc_for_phrase[group][key][length_1]<=2:

                                      new_documents_list.update({key:relevant_doc_for_phrase[group][key]})
                    if new_documents_list=={}:
                       return None
                  except KeyError:
                    return None
                  if self.phrase_index_instance.has_key(group_counter):
                     self.phrase_index_instance[group_counter]=new_documents_list
                  else:

                     self.phrase_index_instance.update({str(group_counter):new_documents_list})

            else:

                if relevant_doc_for_phrase[group]:

                    prev_phrase_group_document_list=relevant_doc_for_phrase[group]
                    prev_phrase_group_document_set=set(relevant_doc_for_phrase[group])
                    self.phrase_index_instance.update(relevant_doc_for_phrase)
                else:
                    return None


        return self.phrase_index_instance[str(group_counter)]

    def process_phrase_group(self,group_number,phrase_group,distance):


        relevant_documents={}
        match_count=0
        word_1_hash={}
        word_2_hash={}
        is_word_1_grp=0
        is_word_2_grp=0

        if  phrase_group:

                if len(phrase_group)==1:
                    relevant_documents.update({group_number:self.return_query_results(phrase_group[0])})
                if self.phrase_index_instance.has_key(phrase_group[0]):

                   is_word_1_grp=1
                   word_1_hash=self.phrase_index_instance[phrase_group[0] ]

                else:

                   word_1_hash=self.return_query_results(phrase_group[0])

                if len(phrase_group)==1:
                   relevant_documents.update({group_number:word_1_hash})
                   return relevant_documents

                if self.phrase_index_instance.has_key(phrase_group[1]):
                   is_word_2_grp=1
                   word_2_hash=self.phrase_index_instance[phrase_group[1] ]
                else:
                   word_2_hash=self.return_query_results(phrase_group[1])


                if word_1_hash==None or word_2_hash== None:
                   return None
                common_documents_list=""
                common_documents_list=(set(word_1_hash)).intersection(set(word_2_hash))
                #print common_documents_list
                if common_documents_list:
                   for document in common_documents_list:
                       match_count=0
                       match_positions=[]

                       for position1 in word_1_hash[document][1:] :
                           for position2 in word_2_hash[document][1:] :
                                 check_distance=0
                                 if is_word_1_grp==0 or is_word_2_grp==0:
                                    check_distance=distance
                                 else:
                                     check_distance=2

                                 if position1-position2==check_distance:
                                     match_pos=0
                                     match_count=match_count+1

                                     pos=position2
                                     match_positions.append(pos)
                       if match_count>=1:
                            position_array=[match_count]
                            position_array.extend(match_positions)
                            new_position={document:position_array}
                            if relevant_documents.has_key(group_number):
                               relevant_documents[group_number].update(new_position)
                            else:
                                relevant_documents.update({group_number:new_position})

                else:

                   return  None

        return relevant_documents






