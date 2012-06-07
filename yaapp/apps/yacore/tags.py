

def clean_tags(tags):
    cleaned_tags = []
    for tag in tags:
        tag = tag.strip()
        if len(tag) == 0:
            continue
        cleaned_tags.append(tag)
    return cleaned_tags