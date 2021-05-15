import pickle
from index import Posting

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

def termAtATimeRetrieval(query, index, k):
    '''
    takes in inputs and returns top k documents that match the query]
    '''
    accumulators = dict()                   # structure -> docId : score
    inverted_lists = []
    results = [] # TODO make priority queue

    query_terms = query.strip('\n').split(' ')             # split query terms
    for term in query_terms:
        inverted_lists.append(index[term])      # sort inverted lists of each term from query
    for list in inverted_lists:
        for posting in list:                    # get postings from inverted lists
            docId = posting.docId
            wordfreq = posting.wordFreq
            if docId not in accumulators:       # create or add scores to documents
                accumulators[docId] = wordfreq
            else:
                accumulators[docId] += wordfreq
    
    # get top k scores
    results =  sorted(accumulators.items(), key=lambda posting: posting[1], reverse=True)
    return results[0:k]


if __name__ == '__main__':
    index = pickle.load(open('indexfile.txt', 'rb'))
    docIds = pickle.load(open('docIds.txt', 'rb'))

    query = input('Search: ').lower()

    while query != "quit":
        top5postings = termAtATimeRetrieval(query, index, 5)

        for posting in top5postings:
            print(docIds[posting[0]])
        query = input('Search: ').lower()

