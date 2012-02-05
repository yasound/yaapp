import metaphone
import settings as yaref_settings
import string

exclude = set(string.punctuation)
def _remove_punctuation(s):
    return ''.join(ch for ch in s if ch not in exclude)

def get_simplified_name(s):
    """
    return simplified name : remove multiple spaces, eol, tabs and punctuations and lower everything
    """
    return ' '.join(_remove_punctuation(s).split()).lower()

def _is_digit(val):
    """
    return true if val is a digit (s.is_digit() fail with unicode
    """
    try:
        int(val)
        return True
    except ValueError:
        return False
    
def build_dms(sentence, remove_common_words=False):
    dms = []
    if not sentence:
        return dms
    sentence = _remove_punctuation(sentence)
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