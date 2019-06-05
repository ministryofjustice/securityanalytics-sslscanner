import os
import aioboto3
import boto3
from utils.lambda_decorators import ssm_parameters, async_handler
from utils.json_serialisation import dumps
from json import loads
from datetime import datetime
import subprocess

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]
task_name = os.environ["TASK_NAME"]
ssm_prefix = f"/{app_name}/{stage}"
ssm_client = aioboto3.client("ssm", region_name=region)
sqs_client = boto3.client("sqs", region_name=region)
SQS_PUSH_URL = f"{ssm_prefix}/tasks/{task_name}/task_queue/url"


def run_task(event, sns_rec):
    msg = loads(sns_rec['Message'])
    if 'ports' in msg.keys():
        for port_data in msg['ports']:
            if port_data['port_id'] == '443' or port_data['service'] == 'https':
                scan = {}
                scan["target"] = f"{msg['address']}:{port_data['port_id']}"
                scan["address"] = msg["address"]
                scan["address_type"] = msg["address_type"]
                # TODO: replace this with a consistent identifier later
                scan["scan_end_time"] = msg["scan_end_time"]
                print(scan)
                reponse = sqs_client.send_message(
                    QueueUrl=event["ssm_params"][SQS_PUSH_URL],
                    MessageBody=dumps(scan)
                )


@ssm_parameters(
    ssm_client,
    SQS_PUSH_URL
)
@async_handler
async def check_event(event, _):
    for record in event["Records"]:
        run_task(event, record["Sns"])
