from constants import REQUIRED_TAGS


def normalize_tags(tags):

    if not tags:
        return {}

    return {
        tag["Key"]: tag["Value"]
        for tag in tags
    }


def get_missing_tags(tags):

    tag_map = normalize_tags(tags)

    missing = []

    for required_tag in REQUIRED_TAGS:
        if required_tag not in tag_map:
            missing.append(required_tag)

    return missing


def is_protected(tags):

    tag_map = normalize_tags(tags)

    return tag_map.get("Protected") == "true"