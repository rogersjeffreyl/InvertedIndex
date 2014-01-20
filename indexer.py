__author__ = 'rogersjeffrey'


from xml.dom import minidom
import cPickle as pickle
import  os.path
import indexutils

"""
 This class  provides methods for  constructing the index form the corpora. The index is a dictionary that is serialized
 on to the disk using pickle and reloaded back into memory using query processing

 The index dictionary  is of the following format

         The index dicitonary looks like this

         { <Word> :

                  {
                    <DOC1ID> :[count,pos1,pos2,pos3] ,
                    <DOC2ID> :[count,pos1,pos2,pos3]

                  }
         }

 For each word that is read from the test corpus it creates a list  having the documents and the positions in the document
 where the word occurred
"""
class indexer:

  def __init__(self,documentPaths):

      self.docs=[documentPaths]
      # word index dictionary
      self.indexDictionary={}
      # document index dictionary
      self.documentIndex={}
      #total words
      self.total_words=0
      #total stop words
      self.total_stop_words=0
      # siz of index file
      self.index_file_size=""
      # no of stemmed words
      self.number_of_stemmed_words=0
      # number of documents in the corpora
      self.total_documents=0


  # this method parses the document which is is xml format and retrieves the content of the document
  def get_document_content(self,documentPath):

      return minidom.parse(documentPath)

  # this method tokenizes the document text into words removing punctuations other than '-'
  def tokenize_document_text(self,documentContent):
      return indexutils.tokenize_string_without_punctuations(documentContent)

  #  this methods is used to update the the index dictionary after reading a document
  #  For an existing word the  index is updated with the  new document details
  #  For a new words not in the index a new entry is created
  def update_index_dictionaries(self,documentDetails,tokenCountHash):
      for token in tokenCountHash:
          documentId=str(documentDetails[0])
          documentHash={}
          token=token.lower()
          if self.indexDictionary.has_key(token):
             # Processing if a word exists in a document
             documentListForToken={}
             documentListForToken=self.indexDictionary[token]
             if(documentListForToken.has_key(documentId)):
                # If Doc already exists update the details accordingly
                self.indexDictionary[token][documentId]=tokenCountHash[token]
             else:

                 documentHash=self.indexDictionary[token]
                 documentHash.update({documentId:tokenCountHash[token]})
                 self.indexDictionary.update({str(token):documentHash})
          else:
            # If word does not exist then update with new details
            position_list=[]
            position_list=list(tokenCountHash[token])
            documentHash.update({documentId:position_list})
            self.indexDictionary.update({str(token):documentHash})
  # This method parses the xml documents and constructs the index hash
  def populate_index_hash(self):
      file_list=""
      index=""
      tokenCountHash={}
      count=0
      # For every path supplied as corpus path
      for documentPath in self.docs:

          #get list of files in a particular corpus path
          file_list=indexutils.get_files_in_path(documentPath)
          # Calculate the total number of documents in the corpus path
          self.total_documents=self.total_documents+len(file_list)
          # read every file in the corpus
          for file in file_list:


              documentPaths=indexutils.construct_path(documentPath,file)
              documentContent=self.get_document_content(documentPaths)
              documentTitle=""
              documentId=""
              documentAuthor=""
              documentBibilio=""
              # TODO replace the hard coded characters
              # Parse the corpus and extract the text,title, author and bibiliography info
              documentText=str(documentContent.getElementsByTagName('TEXT')[0].firstChild.data.strip())
              documentTitle=str(documentContent.getElementsByTagName('TITLE')[0].firstChild.data.strip())
              documentId=str(documentContent.getElementsByTagName('DOCNO')[0].firstChild.data.strip())
              documentAuthor=str(documentContent.getElementsByTagName('AUTHOR')[0].firstChild.data.strip())
              documentBibilio=str(documentContent.getElementsByTagName('BIBLIO')[0].firstChild.data.strip())

              documentDetails=()
              documentDetails=(documentId,documentTitle,documentAuthor)
              # Split the document into non punctuated  words
              tokens=self.tokenize_document_text(documentText)
              title_token =self.tokenize_document_text(documentTitle)
              tokens=tokens+title_token
              # Each token/word returned by the tokenizer
              tokenCountHash={}
              positionCounter=0
              positionList= []

              # For every token got from corpus file
              for token in tokens:


                self.total_words=self.total_words+1
                  # introduce something here if stemming has to be done here
                #ignore if word is stop word
                if indexutils.return_is_stop_word(token):
                  positionCounter=positionCounter
                  self.total_stop_words=self.total_stop_words+1
                else:
                  positionCounter=positionCounter+1
                  token=token.strip()
                  #else perform stemming
                  new_word=indexutils.return_stemmed_word(token)
                 # if the word has been actually stemmed
                  if(new_word!=token):
                      self.number_of_stemmed_words=self.number_of_stemmed_words+1
                  token=new_word

                  #add the new word to the position list formed, i.e if a word already exists append the new
                  #position to the position list of that word in the file being currently read
                  if tokenCountHash.has_key(token):

                     positionList= tokenCountHash[token]
                     positionList [0]= int(positionList [0])+1
                     positionList.append(positionCounter)
                     tokenCountHash.update({token:positionList})
                  else:

                     positionList=[1]
                     positionList.append(positionCounter)
                     tokenCountHash.update({token:positionList})

              #updating the index dictionary
              self.update_index_dictionaries(documentDetails,tokenCountHash)
              #update the document meta data dictionary
              self.documentIndex.update({documentId:{"path":documentPaths,"title":documentTitle,"author":documentAuthor,"bibliography":documentBibilio}})

  # This stores/serializes the index hash onto the disk
  # Both metadata hash and word index hash are serialized
  def dump_index_hash(self):
     pickle.dump( self.indexDictionary,open("index.p","wb"))
     pickle.dump( self.documentIndex,open("documentindex.p","wb"))

  def print_index_hash(self):
      print self.indexDictionary

  # this prints the statistics of the index
  def get_index_stats(self):
      index_file_size=float(os.path.getsize("documentindex.p"))
      doc_metadata_file_size=float(os.path.getsize("index.p"))

      print "Index File Size                                      :%f  MB" %(index_file_size/(1024*1024))
      print "Total words(includes repetitions)                    :%d" %(self.total_words)
      print "Unique Indexed Words                                 :%d" %(len(self.indexDictionary))
      print "Total stop word occurences                           :%d" %(self.total_stop_words)
      print "Total stem words                                     :%d" %(self.number_of_stemmed_words)
      print "Total corpus files                                   :%d" %(self.total_documents)










