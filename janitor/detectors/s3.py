from botocore.exceptions import ClientError

from detectors.tags import missing_tag_finding


def detect_untagged_buckets(s3_client):
    findings = []

    response = s3_client.list_buckets()

    for bucket in response.get("Buckets", []):
        bucket_name = bucket["Name"]

        try:
            tag_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = tag_response.get("TagSet", [])
        except s3_client.exceptions.NoSuchTagSet:
            tags = []
        except s3_client.exceptions.NoSuchBucket:
            continue
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code")

            if code == "NoSuchTagSet":
                tags = []
            elif code == "NoSuchBucket":
                continue
            else:
                raise

        tag_finding = missing_tag_finding(bucket_name, "s3_bucket", tags)

        if tag_finding:
            findings.append(tag_finding)

    return findings
