import pickle
from index import Posting, resetFiles
from index import Item
# from index import convertToPostings
import time
from index import count_files
from index import urls_foldername
import math
import sys

merged_filename = 'data/merged.txt'

file_count = count_files(urls_foldername)
docIds = pickle.load(open('data/docIds.txt', 'rb'))
alphaIndex = pickle.load(open('data/alphaIndex.txt', 'rb'))

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
                'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 
                'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
                'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 
                'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 
                'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 
                'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 
                'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 
                'won', "won't", 'wouldn', "wouldn't"]


# def documentAtATimeRetrieval(query, index, f, g, k):
#     '''
#     takes in inputs and returns top k documents that match the query.
#     f - document feature function
#     g - query feature function
#     '''
#     array = []
#     results = [] # stores matching documents
#     query_postings = []

#     terms = query.split(' ')
#     for term in terms:
#     #     query_postings.append(index[term])
#     # for i in range(num_docs):
#     #     for j in range(len(terms)):
        


#     return

# [(1, 1), (12, 1), (273, 1), (1040, 1), (1840, 1), ]

def termAtATimeRetrieval(query, indexfilename, alphaIndex, k):
    '''
    takes in inputs and returns top k documents that match the query]
    '''
    accumulators = dict()                   # structure -> docId : score
    inverted_lists = []
    results = [] # TODO make priority queue
    list_of_docIDs = []

    indexfile = open(indexfilename, 'r')

    query_terms = query.strip('\n').split()             # split query terms
    [word for word in query_terms if word not in stopwords]
    for term in query_terms:
        li, ids = findTermInFile(term, indexfile, alphaIndex)
        inverted_lists.append(li)                           # store inverted lists of each term from query (only scoring documents that contain query terms)
        list_of_docIDs.append(ids)
    list = intersectPostings(inverted_lists, list_of_docIDs)
    # print(inverted_lists)
    for postings in list:
        for key, value in postings.items():                    # get postings from inverted lists
    # for posting in list: 
            docId = key
            wordfreq = value[0]
            importance_weight = value[1]
            tfidf = ((1 + math.log(int(wordfreq))) * math.log(file_count/len(postings))) * int(importance_weight)
            if docId not in accumulators:       # create or add scores to documents
                accumulators[docId] = tfidf
            else:
                accumulators[docId] += tfidf
    
    indexfile.close()
    # get top k scores
    results =  sorted(accumulators.items(), key=lambda posting: posting[1], reverse=True)
    return results[0:min(len(results), k)]

# HELPER FUNCTIONS
def findTermInFile(term: str, indexfile, alphaIndex: dict()):
    ''' finds term in merged index file'''
    t0 = time.time()

    letter = term[0]
    start = alphaIndex[letter]
    
    indexfile.seek(start)
    while True:
        line = indexfile.readline().split()
        
        token = line[0]

        if token == term:
            postings, docIds = convertToPostings(line[1:])
            # print('found')
            t1 = time.time()
            total_time = (t1-t0) * 1000
            print(f'finding term time {total_time}')
            return postings, docIds

def convertToPostings(array: list):
    ''' takes in list of elements and converts them into pairs of postings'''
    postings = dict()
    docIds = []
    for i in range(0, len(array), 3):
        # postings.append(Posting(array[i], array[i+1]))
        postings[array[i]] = [array[i+1], array[i+2]]
        docIds.append(array[i])
    return postings, docIds

def intersectPostings(inverted_lists: list, list_of_docIds: list):
    ''' intersects (AND) posting list starting from smallest to largest list based off docIds '''
    t0 = time.time()

    list_of_docIds.sort(key=lambda x:len(x))

    new_inverted_lists = []

    temp = set(list_of_docIds[0])
    for i in range(1, len(list_of_docIds)):
        temp = temp & set(list_of_docIds[i])
    for i in range(len(inverted_lists)):
        posting = dict()
        for j in temp:
            posting[j] = inverted_lists[i][j]
        new_inverted_lists.append(posting)

    # print(temp)
    # print(new_inverted_lists)
    t1 = time.time()
    total_time = (t1-t0) * 1000
    print(f'intersection time {total_time}')

    return new_inverted_lists

def search(query):
    ''' wrapper for web gui, query is string input from user '''
    t0 = time.time()

    query = query.lower()

    # get top 5 results from term at a time retrieval
    toppostings = termAtATimeRetrieval(query, merged_filename, alphaIndex, 20)

    # end timer
    t1 = time.time()
    total_time = (t1-t0) * 1000

    return toppostings, total_time
        


if __name__ == '__main__':
    # index = pickle.load(open('indexfile.txt', 'rb'))
    docIds = pickle.load(open('data/docIds.txt', 'rb'))
    alphaIndex = pickle.load(open('data/alphaIndex.txt', 'rb'))
    file_count = count_files(urls_foldername)
    print(file_count)

    # query_terms = sys.argv[1:]

    query = input('Search: ').lower()

    while query != "quit":
        # start timer 
        t0 = time.time()

        toppostings, total_time = search(query)

        # print out results
        for posting in toppostings:
            print(docIds[int(posting[0])])
        print(f"search took {total_time} milliseconds.")

        # prompt user for next query
        query = input('Search: ').lower()



