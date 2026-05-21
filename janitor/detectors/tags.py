from constants import REQUIRED_TAGS


def has_required_tags(tags):

    tag_map = {
        tag["Key"]: tag["Value"]
        for tag in tags
    } if tags else {}

    missing = []

    for required_tag in REQUIRED_TAGS:
        if required_tag not in tag_map:
            missing.append(required_tag)

    return missing