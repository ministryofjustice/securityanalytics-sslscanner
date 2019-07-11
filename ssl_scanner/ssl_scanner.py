import io
import subprocess
from shared_task_code.lambda_scanner import LambdaScanner
from json import loads
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from utils.time_utils import iso_date_string_from_timestamp


class SslScanner(LambdaScanner):
    def __init__(self):
        super().__init__()
        self._dynamodb_param = f"{self.ssm_source_stage_prefix}/scheduler/dynamodb/resolved_addresses/id"

    def ssm_parameters_to_load(self):
        return super().ssm_parameters_to_load() + [
            self._dynamodb_param
        ]

    def get_hosts(self, address, db_name):
        # get the hostname(s) that correspond with the input IP address
        # you can still manually pass through a hostname, which will return an
        # empty array
        print(f"Resolving hosts associated with IP")
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(db_name)
        response = table.query(KeyConditionExpression=Key("Address").eq(address))
        print(f"dns response {response}")
        hosts = {}
        latest_time = 0
        for item in response["Items"]:
            if item["DnsIngestTime"] > latest_time:
                latest_time = item["DnsIngestTime"]
                hosts = item["Hosts"]
        ret = []
        for host in hosts:
            if host[-1] == ".":
                host = host[:-1]
            ret.append(host)
        print(address, ret)
        return ret

    async def scan(self, scan_request_id, scan_request):
        scan_request = loads(scan_request)
        msg = loads(scan_request["Message"])
        if msg["port_id"] == "443" or msg["service"] == "https":
            print(f"address {msg['address']}")
            host_names = self.get_hosts(msg["address"], self.get_ssm_param(self._dynamodb_param))
            print(host_names)
            for host in host_names:
                target = f"{host}:{msg['port_id']}"
                msg["target"] = target
                scan_start_time = iso_date_string_from_timestamp(datetime.now().timestamp())
                print(f"open ssl scan: {target} for request id {scan_request_id}")
                print("running openssl")
                cmd = f"openssl s_client -showcerts -connect {target}"
                merged_file = io.BytesIO()
                try:
                    # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later
                    out = subprocess.check_output(f"{cmd} </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)
                except subprocess.CalledProcessError as e:
                    # openssl will generate an error if there"s a problem in the chain
                    # that is used to source the error info and we do want to suppress this exception
                    pass
                scan_end_time = iso_date_string_from_timestamp(datetime.now().timestamp())
                with open("/tmp/tty2.txt", "r") as f:
                    merged_file.write(f.read().encode("UTF-8"))
                with open("/tmp/tty1.txt", "r") as f:
                    merged_file.write(f.read().encode("UTF-8"))

                merged_file.seek(0)
                await self.write_results_set(
                    f"{scan_request_id}-{host}",
                    merged_file,
                    ".txt",
                    msg,
                    scan_start_time,
                    scan_end_time
                )
        else:
            print("Ignoring non 443 or https service")
