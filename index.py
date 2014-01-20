__author__ = 'rogersjeffrey'
"""
 This program  constructs the index  by reading from the test corpus files
 this accepts the path to the index file as an argument
"""
from sys import argv
import indexutils
import indexer
print "Enter the path of the training corpus"
file_path=raw_input("Corpus Files Path:")
index_start_time=indexutils.gettime()
print "Starting Indexing......."
indexer=indexer.indexer(file_path)
indexer.populate_index_hash()
indexer.dump_index_hash()
print "Indexing Ended"
index_end_time=indexutils.gettime()
print "Time taken to build the index: %f seconds" %(index_end_time-index_start_time)
print "Index Stats:"
indexer.get_index_stats()



