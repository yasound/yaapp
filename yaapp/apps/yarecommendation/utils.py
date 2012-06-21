def sim_distance(doc1, doc2):
    # Get the list of shared_items
    si = {}
    for item in doc1.get('classification').keys():
        if item in doc2.get('classification').keys():
            si[item] = 1
    # if they have no ratings in common, return 0
    if len(si) == 0: return 0
    # Add up the squares of all the differences
    sum_of_squares = sum([pow(doc1['classification'][item] - doc2['classification'][item], 2)
                        for item in doc1['classification'] if item in doc2['classification']])
    return 1 / (1 + sum_of_squares)

# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def top_matches(docs, doc, n=5, similarity=sim_distance):
    scores = [(similarity(doc, other), other.get('db_id')) for other in docs if other != doc]

    # Sort the list so the highest scores appear at the top scores.sort( )
    scores.sort()
    scores.reverse()
    limit =  scores[0:n]
    return [db_id for (_score, db_id) in limit]
