from models import Continent, Country
def _convert_to_utf8(str):
    try:
        encoded_str = str.decode("iso-8859-1").encode("UTF-8")
        return encoded_str
    except:
        return str

def import_continent(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radioways_id, sigle, fr, uk, es, de) = content

        continent, _created = Continent.objects.get_or_create(radioways_id=radioways_id)
        continent.sigle = sigle
        continent.radioways_id = radioways_id
        continent.name_fr = fr
        continent.name_uk = uk
        continent.name_es = es
        continent.name_de = de
        continent.save()

def import_country(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radioways_id, continent_id, sigle, fr, uk, es, de) = content
        continent = Continent.objects.get(radioways_id=continent_id)
        country, _created = Country.objects.get_or_create(radioways_id=radioways_id, defaults={'continent':continent})
        country.sigle = sigle
        country.radioways_id = radioways_id
        country.name_fr = fr
        country.name_uk = uk
        country.name_es = es
        country.name_de = de
        country.save()
