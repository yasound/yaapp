#import metaphone
import settings as yasearch_settings
import string
import re
import unicodedata
from unidecode import unidecode

from fuzzywuzzy import fuzz
import fuzzy

REG_TOKEN = re.compile("[\w\d]+")

exclude = string.punctuation
exclude_regex = re.compile(r"[%s]" % re.escape(exclude))
def _replace_punctuation_with_space(s):
    """
    """
    return exclude_regex.sub(u" ", s)

def get_simplified_name(s):
    """
    return simplified name : 
    * remove multiple spaces, eol, tabs and punctuations 
    * lower everything
    * return unicode
    """
    if s is None:
        return None
    
    if not isinstance(s, unicode):
        s = unicode(s, 'utf-8')
    s = ' '.join(_replace_punctuation_with_space(s).split()).lower()
    return unidecode(s).lower()


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
        if remove_common_words and (word in yasearch_settings.FUZZY_COMMON_WORDS or (not _is_digit(word) and len(word) <= 2)):
            continue 
        if _is_digit(word):
            value = word
            if value not in dms:
                dms.append(value)
        else:
            dmeta = fuzzy.DMetaphone()
            dm = dmeta(word.encode('utf-8'))
            value = dm[0]
            if value is not None and value not in dms:
                dms.append(value)
            value = dm[1]
            if value is not None and value not in dms:
                dms.append(value)
    return dms

        
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

    