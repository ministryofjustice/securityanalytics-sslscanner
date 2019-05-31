from lambda_decorators import async_handler
import os
import boto3
from utils.lambda_decorators import ssm_parameters
from utils.json_serialisation import dumps
from json import loads
from utils.objectify_dict import objectify
import tarfile
import re
import io
import untangle
import datetime
import pytz
from urllib.parse import unquote_plus
import importlib.util
from utils.scan_results import ResultsContext

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]
task_name = os.environ["TASK_NAME"]
ssm_prefix = f"/{app_name}/{stage}"
ssm_client = boto3.client("ssm", region_name=region)
s3_client = boto3.client("s3", region_name=region)
sns_client = boto3.client("sns", region_name=region)

SNS_TOPIC = f"{ssm_prefix}/tasks/{task_name}/results/arn"


def post_results(topic, doc_type, document):
    r = sns_client.publish(
        TopicArn=topic, Subject=doc_type, Message=dumps(document)
    )
    print(f"Published message {r['MessageId']}")


def process_results(topic, bucket, key):
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    content = obj["Body"].read()
    metadata = obj["Metadata"]
    chain = {'records': []}
    for metakey in metadata:
        # strip out the header that AWS adds
        chain[metakey.replace('x-amz-meta-', '')] = metadata[metakey]
    tar = tarfile.open(mode="r:gz", fileobj=io.BytesIO(content), format=tarfile.PAX_FORMAT)
    result_file_name = re.sub(r"\.tar.gz$", "", key.split("/", -1)[-1])
    body = tar.extractfile(result_file_name).read().decode('utf-8').split('\n')
    is_root_ca = True
    start_time, end_time = chain["scan_end_time"], chain["scan_end_time"]
    scan_id = os.path.splitext(result_file_name)[0]
    if len(body) > 0 and ('error' in body[0]):
        # write the error out to elastic
        non_temporal_key = {
            "address": chain['address'],
            "address_type": chain['address_type'],
            "ssl_chain": "No SSL"
        }
        results_context = ResultsContext(topic, non_temporal_key, scan_id, start_time, end_time, task_name, sns_client)

    else:
        for line in body:
            if 'depth' in line:
                record = {}
                params = re.split(r',\s+(?=(?:(?:[^"]*"){2})*[^"]*$)', line.split(' ', 1)[1].replace('\n', ''))
                record['depth'] = int(line.split('depth=')[1].split(' ')[0])
                record['rootCA'] = is_root_ca
                # Top of returned values is always root, first time round the loop it'll be True
                is_root_ca = False
                for param in params:
                    psplit = param.split(' = ')
                    record[psplit[0]] = psplit[1]
                chain['records'].append(record)
            if 'DONE' in line:
                break

        non_temporal_key = {
            "address": chain['address'],
            "address_type": chain['address_type'],
            "ssl_chain": "Valid"
        }
        # TODO store start_time correctly
        # TODO end_time will be correct once the scheduler is in place to change the key (currently end_time is used)

        results_context = ResultsContext(topic, non_temporal_key, scan_id, start_time, end_time, task_name, sns_client)

        for cert in chain['records']:
            results_context.push_context({"depth": f"{cert['depth']}", "root_ca": f"{cert['rootCA']}"})
            results = {}
            for element in cert:
                if (element is not "depth") and (element is not "rootCA"):
                    results[element] = cert[element]
            results_context.post_results("data", results, include_summaries=True)
            results_context.pop_context()


@ssm_parameters(
    ssm_client,
    SNS_TOPIC
)
@async_handler
async def parse_results(event, _):
    topic = event['ssm_params'][SNS_TOPIC]
    for record in event["Records"]:
        s3_object = objectify(record["s3"])
        bucket = s3_object.bucket.name
        key = unquote_plus(s3_object.object.key)
        process_results(topic, bucket, key)
