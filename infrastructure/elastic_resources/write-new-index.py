import os
import sys
import boto3
from requests_aws4auth import AWS4Auth
import requests
import json

if len(sys.argv[1:]) not in range(6, 8):
    raise ValueError(f"write-new-index.py region app_name task_name index_hash index_file url old_index")

region, app_name, task_name, index_hash, index_file_name, url = sys.argv[1:7]
old_index = sys.argv[7] if len(sys.argv) == 8 else None

credentials = (
    boto3.Session()
    if "AWS_ACCESS_KEY_ID" in os.environ.keys() else
    boto3.Session(profile_name=app_name)
).get_credentials()

aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    "es",
    session_token=credentials.token
)

write_alias = f"{task_name}:data:write"
read_alias = f"{task_name}:data:read"
new_index = f"{task_name}:data:{index_hash}"


def add_new_index(index_file):
    if old_index != new_index:
        r = requests.get(f"https://{url}/{new_index}", auth=aws_auth)

        if not r.status_code == 404:
            print(f"Index {new_index} already existed in elastic, ignoring")
            return

        index_doc = json.load(index_file)
        r = requests.put(f"https://{url}/{new_index}", auth=aws_auth, json=index_doc)

        if not r.ok:
            raise ValueError(f"Failure response creating new index ({r.status_code}): {r.text}")

        print(f"Added new index {new_index}")
    else:
        print(f"Index {new_index} already existed, ignoring")


def update_aliases():
    actions = []
    alias_doc = {
        "actions": actions
    }
    if old_index and old_index != new_index:
        actions.append({"remove": {"index": old_index, "alias": write_alias}})

    actions.append({"add": {"index": new_index, "alias": write_alias}})
    actions.append({"add": {"index": new_index, "alias": read_alias}})

    r = requests.post(f"https://{url}/_aliases", auth=aws_auth, json=alias_doc)

    if not r.ok:
        raise ValueError(f"Failure response updating aliases ({r.status_code}): {r.text}")

    print(f"Updated write alias {write_alias} to point to {new_index}")
    print(f"Added read alias {read_alias} to point to {new_index}")


def re_index():
    if old_index and old_index != new_index:
        re_index_doc = {
          "source": {
            "index": old_index
          },
          "dest": {
            "index": new_index
          }
        }
        r = requests.post(f"https://{url}/_reindex", auth=aws_auth, json=re_index_doc)
        print(f"Re-index result {r.text}")

        if not r.ok:
            raise ValueError(f"Failure response re-indexing ({r.status_code}): {r.text}")

        failures = r.json()["failures"]
        if len(failures) > 0:
            raise ValueError(f"Re-index errors ({failures})")

        print(f"Re-indexing from {old_index} to {new_index}")
        delete_old_index()
    else:
        print(f"Not re-indexing because old and new are the same {old_index} to {new_index}")


def delete_old_index():
    print(f"Deleting {old_index}")
    r = requests.delete(f"https://{url}/{old_index}", auth=aws_auth)

    if not r.ok:
        raise ValueError(f"Failure response when deleting old index ({r.status_code}): {r.text}")

    print(f"Deleted {old_index}")


with open(index_file_name, 'r') as index_file:
    add_new_index(index_file)
    update_aliases()
    re_index()



