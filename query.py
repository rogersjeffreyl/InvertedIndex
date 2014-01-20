__author__ = 'rogersjeffrey'
import query_processor as qp
queryProcessorInstance= qp.QueryProcessor()
queryProcessorInstance.reload_index_file()
print "Enter your Search Query"
print "Press Ctrl+C or x to exit"
print "-h lists the help for this program"

while(True):
    query=raw_input('>')
    if query=="x" or query=="X":
       break
    elif query=="--h" or query =="-h" :
       print "helping you"
    else:
       queryProcessorInstance.process_query(query)
"""
query='!"laminar-flow surfaces at full-scale"'
queryProcessorInstance.process_query(query)

"""
"""
print  "********"
query='"final solution" "laminar-floor"'
queryProcessorInstance.process_query(query)

query='"laminar-floor" "protuberances permissible on laminar-flow surfaces at"'
queryProcessorInstance.process_query(query)
#queryProcessorInstance.categorize_input_query(query)

query='"protuberances permissible on laminar-flow surfaces at full-scale flight reynolds numbers"'
queryProcessorInstance.process_query(query)
"""