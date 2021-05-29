# build the inverted index 

import os
import sys
import re
from bs4 import BeautifulSoup
import json
import time
import pickle
import math
import gc
from operator import attrgetter

# files names:
urls_foldername = './developer'
index_filename = 'data/index.txt'
docIds_filename = 'data/docIds.txt'
alpha_filename = 'data/alphaIndex.txt'
merged_filename = "data/merged.txt"

class Posting:
    def __init__(self, docId, wordFreq, importance):
        self.docId = docId
        self.wordFreq = wordFreq
        self.importance = importance
    def __repr__(self):
        # return repr("Posting: docId=" + self.docId + " wordFreq=" + self.wordFreq)
        return repr( "(" + self.docId + ", " + self.wordFreq + ", " + self.importance + ')')

class Item:
    def __init__(self, token, postings):
        self.token = token
        self.postings = postings

    def __lt__(self, other):
        return self.token < other.token
    def __gt__(self, other):
        return self.token > other.token

def buildIndex(directory):
    '''
    function that takes in directory of files that contain set of text documents
    returns inverted index
    '''
    index = dict()
    docId = 0                                                               # docId starts at 0
    docIds = dict()                                                         # hash of docIds to urls
    count = 1
    num_indices_saved = 0

    for root, subdirectories, files in os.walk(directory):
        for filename in files:                                              # for each document
            filepath = os.path.join(root, filename)
            docId += 1                                                      # increase docId
            with open(filepath, "r", encoding="utf8") as f:
                data = json.load(f)
                url = data['url']
                if url not in docIds.values():                              # if docid not in dict then add new url docid to dict 
                    docIds[docId] = url
            tokens = tokenize(data['content'])
            importantTokens = findImportantTokens(data['content'])          # get hashtable of importance words
            wordFreq = computeWordFrequencies(tokens)                       # returns hashtable of words and frequency of that word in the document
            for token in wordFreq:
                if token in importantTokens:                                # if a token was important (had title, h1 or bold tag) adjust weight of that token
                    weight = importantTokens[token]
                else:
                    weight = 0 
                posting = Posting(docId, wordFreq[token], weight)
                if token not in index:                                      # if token is not in index create new list of posting
                    index[token] = []        
                index[token].append(posting)                                # else just append to current list of postings
            
            # save to file (3)
            if (count % math.ceil(file_count/3) == 0) or (count == file_count):                               # if count is size 1/3 of total number of docs, save partial index to file OR last doc
                num_indices_saved += 1
                partial_index_name = "data/index_" + str(num_indices_saved) + '.txt'
                # print(index)
                saveAndSortIndexToFile(index, partial_index_name)
                del index                                          # clear index after saving
                gc.collect()
                index = dict()
                print("indexing to file '" + partial_index_name + "'")
            count += 1
    return index, docIds

# HELPER FUNCTIONS FOR INDEX
def tokenize(text: str) -> list:
    ''' 
    reads text and returns a list of tokens from that text
    '''
    tokens = []                 

    soup = BeautifulSoup(text, 'html.parser')

    for line in soup.get_text().split('\n'):
        temp = removeNonAlphaChars(line)
        tokens += temp                          # add result

    return tokens

def computeWordFrequencies(tokens: list) -> dict:
    '''
    takes in a list of tokens and returns a dict of tokens and returns
    the number of times it appears in list of tokens.
    '''
    word_freq = dict()
    for token in tokens:                 # O(n)
        if token not in word_freq:       # if token not in map add it    O(1)
            word_freq[token] = 1
        else:
            word_freq[token] += 1        # else if already in map increase counter   O(1)
    return word_freq                     # O(1)

def findImportantTokens(text: str) -> dict:
    ''' 
    takes in html text and finds tokens that are important (from title, h1, and bold tag) and assigns weight to that token 
    returns a dict of tokens and their importance weight as the value
    '''
    importance = dict()

    soup = BeautifulSoup(text, 'html.parser')

    titles = soup.find_all('title')
    headers = soup.find_all('h1')
    bold = soup.find_all('b')

    assignImportance(bold, 1, importance)
    assignImportance(headers, 2, importance)
    assignImportance(titles, 3, importance)

    return importance

def assignImportance(list: list, weight: int, importance: dict) -> dict:
    ''' takes in list of strings and assigns each word a weight, mutates dictionary of tokens and their weights as values '''
    for line in list:
        words = removeNonAlphaChars(line.get_text())
        for word in words:
            importance[word] = weight
    return 


def removeNonAlphaChars(line: str):
    ''' function that takes in a string and removes non alphanumeric characters and returns that string split by words '''
    line = line.lower()
    line = re.sub("[^a-z0-9\s-]", "", line)  # to remove all non alphanumeric characters
    temp = re.findall("[a-z0-9]+", line)

    return temp

# HELPER FUNCTIONS
def count_files(directory):
    count = 0
    for root, subdirectories, files in os.walk(directory):
        for file in files:
            count += 1
    return count

def resetFiles(files):
    '''overwrite files in list to be empty'''
    for filename in files:
        with open(filename, "w") as f:
            f.write("")

def saveAndSortIndexToFile(index: list, filename: str):
    '''
    takes in inverted index that's sorted and saves to disk
    '''
    sortedindex = sorted(index.keys(), key=lambda item: item.lower())
    with open(filename, 'w') as f:
        for item in sortedindex:
            string = f"{item}  "                                                   
            for posting in index[item]:                                             
                string += f" {posting.docId} {posting.wordFreq} {posting.importance}  "
            string += "\n"

            f.write(string)
    return

# MERGER
def twoWayMerge(file1, file2, outputfile):
    ''' takes in two files and merges into one big file '''
    f1 = open(file1, 'r')
    f2 = open(file2, 'r')

    line1 = f1.readline()
    line2 = f2.readline()

    with open(outputfile, "a+") as f:
        while line1 != '' and line2 != '':                  # while files aren't at EOF
            item1 = parseline(line1)                        # get token and postings from line
            item2 = parseline(line2)

            if line1 == '':
                string = createString(item2)            
                f.write(string)
                line2 = f2.readline()
            elif line2 == '':
                string = createString(item1)            
                f.write(string)
                line1 = f1.readline()
            
            # find smallest token and add to new file, read next line 
            elif (item1 < item2):
                string = createString(item1)            
                f.write(string)
                line1 = f1.readline()
            elif (item2 < item1):
                string = createString(item2)
                f.write(string)
                line2 = f2.readline()
            # else if both are same token merge postings and add to file, read next line of both files
            elif (item1.token == item2.token):
                temp = item1.postings + item2.postings
                newItem = Item(item1.token, temp)
                string = createString(newItem)
                f.write(string)

                line1 = f1.readline()
                line2 = f2.readline()

    f1.close()
    f2.close()

# HELPER FUNCTIONS FOR MERGER
def createString(item):
    ''' converts item to string '''
    string = f"{item.token}  "                                        
    for posting in item.postings:                                      
        string += f" {posting.docId} {posting.wordFreq} {posting.importance}  "
    string += "\n"
    return string

def parseline(line):
    ''' takes line that was read from a file and convert to an item '''
    elements = line.split()
    token = elements[0]
    postings = convertToPostings(elements[1:])
    item = Item(token, postings)

    return item

def convertToPostings(array: list):
    ''' takes in list of elements and converts them into postings'''
    postings = []
    # print(array)
    for i in range(0, len(array), 3):
        postings.append(Posting(array[i], array[i+1], array[i+2]))
    return postings


# INDEX THE INDEX (by alphabet)
def indexIndexByAlphabet(filename: str):
    index = dict()
    letter = '0'
    index[letter] = 0
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            if letter != line[0]:                   # on next letter, add to hash table
                letter = line[0]
                index[letter] = f.tell()
            line = f.readline()
    return index



if __name__ == "__main__":
    # reset text files to be empty
    resetFiles([docIds_filename, "data/temp.txt", merged_filename]) # don't know why but when emptying a file it's faster to write to an empty file than just overwriting the file.
    
    # start timer
    t0 = time.time()

    file_count = count_files(urls_foldername)
    print(file_count)

    # build index
    index, docIds = buildIndex(urls_foldername)

    # merge partial indices
    twoWayMerge("data/index_1.txt", "data/index_2.txt", "data/temp.txt")
    twoWayMerge("data/temp.txt", "data/index_3.txt", merged_filename)
    print("partial indices merged.")

    # index the index by alphabet
    alphaIndex = indexIndexByAlphabet(merged_filename)
    indexIndexByAlphabet(merged_filename)

    # dump docIds to a file
    pickle.dump(docIds, open(docIds_filename , 'wb'))
    print("docIds are saved.")

    # dump alpha index to a file
    print(alphaIndex)
    pickle.dump(alphaIndex, open(alpha_filename , 'wb'))
    print("index of index by alphabet is saved.")

    # get end time
    t1 = time.time()

    total_time = (t1-t0)/60
    print(f"program took {int(total_time * 100)/100} minutes.")

'''
references:

https://www.kite.com/python/answers/how-to-list-all-subdirectories-and-files-in-a-given-directory-in-python
https://newbedev.com/how-to-iterate-over-files-in-a-given-directory
https://stackoverflow.com/questions/1316767/how-can-i-explicitly-free-memory-in-python
'''