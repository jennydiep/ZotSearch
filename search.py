def documentAtATimeRetrieval(query, index, f, g, k):
    '''
    takes in inputs and returns top k documents that match the query.
    f - document feature function
    g - query feature function
    '''
    array = []
    results = [] # stores matching documents
    query_postings = []

    terms = query.split(' ')
    for term in terms:
    #     query_postings.append(index[term])
    # for i in range(num_docs):
    #     for j in range(len(terms)):
        


    return