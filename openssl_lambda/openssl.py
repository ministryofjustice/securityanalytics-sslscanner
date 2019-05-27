from lambda_decorators import async_handler
from utils.lambda_decorators import ssm_parameters
import json
import subprocess
import boto3
from datetime import datetime


def start_scan(event, context):
    region = os.environ["REGION"]
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    cmd = "openssl s_client -showcerts -connect "+event['host']+":"+event['port']
    date_string = f'{datetime.now():%Y-%m-%dT%H%M%S%Z}'
    out = subprocess.check_output("echo | "+cmd+" </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)

    # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later
    output = ""
    s3file = event['message_id']+"-"+date_string+"-ssl.txt"
    mergedf = open('/tmp/'+s3file, 'w')
    with open('/tmp/tty2.txt', 'r') as f:
        mergedf.write(f.read())
    with open('/tmp/tty1.txt', 'r') as f:
        mergedf.write(f.read())
    mergedf.close()
    subprocess.check_output(f'cd /tmp;tar -czvf "{s3file}.tar.gz" "{s3file}"', shell=True)

    s3 = boto3.resource('s3', region_name=region)
    s3.Bucket(f'{stage}-{app_name}-ssl-results').upload_file(f"/tmp/{s3file}.tar.gz", f"{s3file}.tar.gz")

    return {
        'statusCode': 200
    }
