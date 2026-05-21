from constants import REQUIRED_TAGS


def normalize_tags(tags):
    if not tags:
        return {}

    return {tag["Key"]: tag["Value"] for tag in tags}


def get_missing_tags(tags):
    tag_map = normalize_tags(tags)
    return [
        required_tag for required_tag in REQUIRED_TAGS if required_tag not in tag_map
    ]


def is_protected(tags):
    tag_map = normalize_tags(tags)
    value = tag_map.get("Protected", "")

    return value.lower() == "true"


def report_tags(tags):
    tag_map = normalize_tags(tags)

    for required_tag in REQUIRED_TAGS:
        tag_map.setdefault(required_tag, None)

    return tag_map


def missing_tag_finding(resource_id, resource_type, tags):
    missing_tags = get_missing_tags(tags)

    if not missing_tags:
        return None

    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "reason": f"missing_tags: {','.join(missing_tags)}",
        "age_days": 0,
        "estimated_monthly_cost_usd": 0.0,
        "tags": report_tags(tags),
        "suggested_action": "add_tags",
        "safe_to_auto_delete": False,
    }
