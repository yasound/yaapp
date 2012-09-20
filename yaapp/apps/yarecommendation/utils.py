from math import sqrt
from math import sqrt
import sys

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

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(doc1, doc2):
    # Get the list of mutually rated items
    si = {}
    for item in doc1.get('classification').keys():
        if item in doc2.get('classification').keys(): si[item] = 1
    # Find the number of elements
    n = len(si)
    # if they are no ratings in common, return 0
    if n == 0: return 0
    # Add up all the preferences
    sum1 = sum([doc1.get('classification')[it] for it in si])
    sum2 = sum([doc2.get('classification')[it] for it in si])
    # Sum up the squares
    sum1Sq = sum([pow(doc1.get('classification')[it], 2) for it in si])
    sum2Sq = sum([pow(doc2.get('classification')[it], 2) for it in si])
    # Sum up the products
    pSum = sum([doc1.get('classification')[it] * doc2.get('classification')[it] for it in si])
    # Calculate Pearson score
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0
    r = num / den
    return r

# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def top_matches(docs, doc, n=5, similarity=sim_distance):
    scores = [(similarity(doc, other), other.get('db_id')) for other in docs if other != doc]

    # Sort the list so the highest scores appear at the top scores.sort( )
    scores.sort()
    scores.reverse()
    limit = scores[0:n]
    return [db_id for (_score, db_id) in limit]

class TailRecurseException:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

def tail_call_optimized(g):
    """
    This function decorates a function with tail call
    optimization. It does this by throwing an exception
    if it is it's own grandparent, and catching such
    exceptions to fake the tail call optimization.

    This function fails if the decorated
    function recurses in a non-tail context.
    """
    def func(self, *args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back \
            and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while 1:
                try:
                    return g(self, *args, **kwargs)
                except TailRecurseException, e:
                    args = e.args
                    kwargs = e.kwargs
    func.__doc__ = g.__doc__
    return func
