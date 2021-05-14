# building the inverted index 

import os
import sys
import re
from bs4 import BeautifulSoup
import json
import time

class Posting:
    def __init__(self, docId, wordFreq):
        self.docId = docId
        self.wordFreq = wordFreq

def buildIndex(directory):
    '''
    function that takes in directory of files that contain set of text documents
    returns inverted index
    '''
    doc_count = 0
    index = dict()
    docId = 0                                                       # docId starts at 0
    docIds = dict()                                                 # hash of docIds to urls

    for root, subdirectories, files in os.walk(directory):
        for filename in files:                                                  # for each document
            filepath = os.path.join(root, filename)
            doc_count += 1
            docId += 1                                                      # increase docId
            # with open(filename, "r", encoding="utf8") as f:
            #     data = json.load(f)
            #     docIds[docId] = data['url']
            tokens = tokenize(filepath)
            wordFreq = computeWordFrequencies(tokens)            # returns hashtable of words and frequency of that word in the document
            for token in wordFreq:
                posting = Posting(docId, wordFreq[token])
                if token not in index:                                      # if token is not in index create new list of posting
                    index[token] = []        
                index[token].append(posting)                                # else just append to current list of postings
            print(f"{doc_count}")
    return index


def tokenize(filename: str) -> list:
    ''' 
    reads text file from filename and returns a list of tokens from that file
    '''
    tokens = []                 
            

    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
        soup = BeautifulSoup(data['content'], 'html.parser')

        for line in soup.get_text().split('\n'):
            line = line.lower()
            line = re.sub("[^a-z0-9\s-]", "", line)  # to remove all non alphanumeric characters
            temp = re.findall("[a-z0-9]+", line)
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

def saveIndexToFile(index: dict):
    '''
    takes in inverted index (hashtable) and saves to disk
    '''
    with open("index.txt", 'a') as f:
        for token in index:
            string = f"{token} ["

            for posting in index[token]:
                string += f"({posting.docId}, {posting.wordFreq}), "
            string += "]\n"

            f.write(string)
    return

if __name__ == "__main__":
    t0 = time.time()
    saveIndexToFile(buildIndex("./analyst"))
    t1 = time.time()

    total_time = (t1-t0)/60
    print(f"program took {int(total_time * 100)/100} minutes.")
'''
references:

https://www.kite.com/python/answers/how-to-list-all-subdirectories-and-files-in-a-given-directory-in-python
https://newbedev.com/how-to-iterate-over-files-in-a-given-directory
'''