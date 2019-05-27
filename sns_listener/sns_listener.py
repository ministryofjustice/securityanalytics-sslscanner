from lambda_decorators import async_handler
import os
import boto3
from utils.lambda_decorators import ssm_parameters

from json import loads
from datetime import datetime
import subprocess

region = os.environ["REGION"]
stage = os.environ["STAGE"]
app_name = os.environ["APP_NAME"]
task_name = os.environ["TASK_NAME"]
ssm_prefix = f"/{app_name}/{stage}"
ssm_client = boto3.client("ssm", region_name=region)
SQS_PUSH_URL = f"{ssm_prefix}/tasks/{task_name}/task_queue/url"

def run_task(event, sns_rec):
    print(event)
    msg = loads(sns_rec['Message'])
    queue = False
    if 'ports' in msg.keys():
        for port_data in msg['ports']:
            print(f"port_id: {port_data['port_id']}, service: {port_data['service']}")
            if port_data['port_id'] == '443' or port_data['service'] == 'https':
                print(f"sending {msg['address']}:{port_data['port_id']} for openssl scan")
                sqs = boto3.client('sqs')
                print(f"SQS_URL: {event['ssm_params'][SQS_PUSH_URL]}")
                reponse = sqs.send_message(
                    QueueUrl=event["ssm_params"][SQS_PUSH_URL],
                    MessageBody=f"{msg['address']}:{port_data['port_id']}"
                )


@ssm_parameters(
    ssm_client,
    SQS_PUSH_URL
)
@async_handler
async def check_event(event, _):
    for record in event["Records"]:
        run_task(event, record["Sns"])
