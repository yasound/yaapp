

def clean_tags(tags):
    cleaned_tags = []
    for tag in tags:
        tag = clean_tag(tag)
        if len(tag) == 0:
            continue
        cleaned_tags.append(tag)
    return cleaned_tags

def clean_tag(tag):
    return tag.strip().lower()
    