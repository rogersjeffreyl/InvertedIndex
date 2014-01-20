__author__ = 'rogersjeffrey'

"""
This module has functions that generate the snippet to be displayed for any given query
The  snippets are highlighted in blue and the title of each document is displayed
If the  query is a not query then no highlighting is done
"""

import indexutils
import commands
import mmap
import indexutils
import re
def print_query_snippet(document_path,query_list):

   generate_snippet_array(document_path,query_list)

# Generates the snippet array to be printed
def generate_snippet_array(filename,query):


    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    snippet=[]
    query_dict={}
    for key, value in query.iteritems():
        for ikey, ivalue in value.iteritems():
            query_dict.setdefault(ikey,{})[key] = ivalue


    with open(filename, "r+") as f:
        real_snippet=""
        # memory-map the file, size 0 means whole file
        map1 = mmap.mmap(f.fileno(), 0)
        # go to begining of file and read file
        map1.seek(0)
        snippet=" ".join(indexutils.tokenize_string_without_punctuations(str(map1[:]).replace("\n"," ")))
        #  match the title
        match= re.match(r'.*TITLE(.*)TITLE', snippet)
        title=match.group(1)

        # for each query formulate snippet
        for query in query_dict:
            new_query=query.strip()
            new_query=" ".join(new_query.split())
            title=title.replace(query,OKBLUE+query+ENDC)
            for keys in query_dict[query].keys():
                if keys=="PHRASE":
                   query=query.strip('"')
                if keys!="NOT":

                    match= re.match(r'.*TEXT(.*)TEXT', snippet )
                    if match:
                       text=match.group(1)
                       real_snippet=text.replace(query,OKBLUE+query+ENDC)
                else:
                    # Print the document text if no match is  found
                    match= re.match(r'.*TEXT(.*)TEXT', snippet )
                    text=match.group(1)
                    real_snippet=text

        map1.close()

        counter=0
        final_snippet=""
        print "TITLE:"+title+"\n"
        for snippet_word in real_snippet.split():
            counter=counter+1
            if counter%15==0:
               print final_snippet
               final_snippet=""
            else:
               final_snippet=final_snippet+" "+snippet_word
    return  snippet
