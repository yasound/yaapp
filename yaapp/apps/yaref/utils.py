import metaphone
import settings as yaref_settings
import gc
import string
import re
import unicodedata
from fuzzywuzzy import fuzz
REG_TOKEN = re.compile("[\w\d]+")

exclude = string.punctuation
exclude_regex = re.compile(r"[%s]" % re.escape(exclude))
def _replace_punctuation_with_space(s):
    """
    """
    return exclude_regex.sub(" ", s)

def get_simplified_name(s):
    """
    return simplified name : 
    * remove multiple spaces, eol, tabs and punctuations 
    * lower everything
    * convert to ascii
    """
    s = ' '.join(_replace_punctuation_with_space(unicode(s)).split()).lower()
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')    

def _is_digit(val):
    """
    return true if val is a digit (s.is_digit() fail with unicode
    """
    try:
        int(val)
        return True
    except ValueError:
        return False
    
def build_dms(sentence, remove_common_words=False, exceptions_list=None):
    dms = []
    if not sentence:
        return dms
    if sentence == exceptions_list:
        remove_common_words = False
    sentence = _replace_punctuation_with_space(sentence)
    words = sorted(sentence.lower().split())
    for word in words:
        if remove_common_words and (word in yaref_settings.FUZZY_COMMON_WORDS or (not _is_digit(word) and len(word) <= 2)):
            continue 
        if _is_digit(word):
            value = word
        else:
            dm = metaphone.dm(word)
            value = u'%s - %s' % (dm[0], dm[1])
            if value == u' - ':
                continue
        if value not in dms:
            dms.append(value)
    return dms

def convert_filename_to_filepath(filename):
    """
    123456789.jpg --> 123/456/789.jpg
    """
    if len(filename) != len('123456789.jpg'):
        return None
    part1 = filename[:3]
    part2 = filename[3:6]
    part3 = filename[6:9]
    extension = filename[-3:]
    return '%s/%s/%s.%s' % (part1, part2, part3, extension)
    
def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()
        
def token_set_ratio(s1, s2, method):

    if s1 is None: raise TypeError("s1 is None")
    if s2 is None: raise TypeError("s2 is None")

    # pull tokens
    tokens1 = set(REG_TOKEN.findall(s1))
    tokens2 = set(REG_TOKEN.findall(s2))

    intersection = tokens1.intersection(tokens2)
    diff1to2 = tokens1.difference(tokens2)
    diff2to1 = tokens2.difference(tokens1)

    sorted_sect = u" ".join(sorted(intersection))
    sorted_1to2 = u" ".join(sorted(diff1to2))
    sorted_2to1 = u" ".join(sorted(diff2to1))

    combined_1to2 = sorted_sect + " " + sorted_1to2
    combined_2to1 = sorted_sect + " " + sorted_2to1

    # strip
    sorted_sect = sorted_sect.strip()
    combined_1to2 = combined_1to2.strip()
    combined_2to1 = combined_2to1.strip()

    pairwise = [
        fuzz.ratio(sorted_sect, combined_1to2),
        fuzz.ratio(sorted_sect, combined_2to1),
        fuzz.ratio(combined_1to2, combined_2to1)
    ]
    ratio = 0
    if method == 'min':
        ratio = min(pairwise)
    elif method == 'mean':
        ratio = sum(pairwise) / len(pairwise)
    else:
        ratio = max(pairwise)
    return ratio

    