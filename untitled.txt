Steps to run the Code

1)Run the indexer first using python index.py
  The user will be prompted to enter the path of corpus. Enter the path there

2) For querying run the query.py as python query.py  
  
  
Modules:
indexer.py - Contains the main functions for indexing 
index_utils.py- contains utilitiy methods like tokenizing, stemming and stopwords checker
query.py- Forms the user interface for querying
query_processor.py-Contains the modules that process the input queries and display the results. It also has methods for  the tf,df,freq,similar commands
result_formatter.py- hash the  functions that are responsible for printing the snippet 
  