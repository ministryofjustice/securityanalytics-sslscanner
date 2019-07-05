import io
import subprocess
from shared_task_code.lambda_scanner import LambdaScanner
from .host_validation import is_valid_hostname
from json import loads
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from utils.time_utils import iso_date_string_from_timestamp


class SslScanner(LambdaScanner):
    def __init__(self):
        self._dynamodb_param = "/scheduler/dynamodb/resolved_addresses/id"

        super().__init__([self._dynamodb_param])

    def get_hosts(self, addr, db_name):
        # get the hostname(s) that correspond with the input IP address
        # you can still manually pass through a hostname, which will return an
        # empty array
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(db_name)
        response = table.query(KeyConditionExpression=Key('Address').eq(addr))
        hosts = {}
        latest_time = 0
        for item in response['Items']:
            if item['DnsIngestTime'] > latest_time:
                latest_time = item['DnsIngestTime']
                hosts = item['Hosts']
        ret = []
        for host in hosts:
            if host[-1] == '.':
                host = host[:-1]
            ret.append(host)
        print(addr, ret)
        return ret

    # def build_hosts(event, scan_input):
    #     # take the input address, and check in our dynamoDB for all the host names
    #     # associated with it so that each one can be scanned individually
    #     scans = []
    #     if not isinstance(scan_input, dict):
    #         # manual invocation - create the bare minimum object needed if this was
    #         # triggered through the normal flow
    #         base_rec = {"target": scan_input, "address": scan_input, "address_type": "ipv4"}
    #     else:
    #         base_rec = scan_input
    #     if not is_valid_hostname(base_rec["target"]):
    #         raise ValueError(
    #             f"Invalid hostname and/or port for openssl task {scan['target']}")
    #         return
    #     host = base_rec["target"].split(':')[0]
    #     port = base_rec["target"].split(':')[1]
    #     hostnames = get_hosts(host, event['ssm_params'][ssm_prefix+ADDRESS_TABLE])
    #     if hostnames == []:
    #         # if we don't know about this host yet, it might have been a manual invocation
    #         # so write the input to the array so it gets scanned
    #         hostnames.append(host)
    #     for hostname in hostnames:
    #         base_rec["target"] = hostname+":"+port
    #         scans.append(copy.deepcopy(base_rec))
    #     return scans

    async def scan(self, scan_request_id, scan_request):
        scan_request = loads(scan_request)
        print(scan_request)
        msg = loads(scan_request["Message"])
        if msg["port_id"] == "443" or msg["service"] == "https":
            print(f"address {msg['address']}")
            hostnames = self.get_hosts(msg['address'], self.get_ssm_param(self._dynamodb_param))
            print(hostnames)
            index = 0
            for host in hostnames:
                target = host+":"+msg["port_id"]
                msg["target"] = target
                scan_start_time = iso_date_string_from_timestamp(datetime.now().timestamp())
                print(f"open ssl scan: {target} for request id {scan_request_id}")
                print('running openssl')
                cmd = f"openssl s_client -showcerts -connect {target}"
                mergedf = io.BytesIO()

                try:
                    out = subprocess.check_output(
                        f"echo | {cmd} </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)
                    # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later

                except subprocess.CalledProcessError as e:
                    # openssl will generate an error if there's a problem in the chain - just get the output and do something with it
                    pass
                scan_end_time = iso_date_string_from_timestamp(datetime.now().timestamp())
                with open("/tmp/tty2.txt", "r") as f:
                    mergedf.write(f.read().encode('UTF-8'))
                with open("/tmp/tty1.txt", "r") as f:
                    mergedf.write(f.read().encode('UTF-8'))

                mergedf.seek(0)
                await self.write_file(f"{scan_request_id}-{index}", scan_request, mergedf, ".txt", msg, scan_start_time, scan_end_time)

        return None, "", None
        #     scan = {"target": f'{port_data["Data"]["address"]}:{port_data["Data"]["port_id"]}',
        #             "address": port_data["Data"]["address"],
        #             "address_type": port_data["Data"]["address_type"]}
        # if "ports" in msg.keys():
        #     for port_data in msg["ports"]:
        #         if port_data["Data"]["port_id"] == "443" or port_data["Data"]["service"] == "https":
        #             scan = {"target": f'{port_data["Data"]["address"]}:{port_data["Data"]["port_id"]}',
        #                     "address": port_data["Data"]["address"],
        #                     "address_type": port_data["Data"]["address_type"]}
        #             sns_listener.sendToSQS(scan)

        # target = scan_request["target"]

        # if not is_valid_hostname(target):
        #     raise ValueError(
        #         f"Invalid hostname and/or port for openssl task {target}")

        # print(f"open ssl scan: {scan_request['target']} for request id {scan_request_id}")
        # print('running openssl')
        # cmd = f"openssl s_client -showcerts -connect {target}"
        # mergedf = io.BytesIO()

        # try:
        #     out = subprocess.check_output(f"echo | {cmd} </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)
        #     # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later

        # except subprocess.CalledProcessError as e:
        #     # openssl will generate an error if there's a problem in the chain - just get the output and do something with it
        #     pass

        # with open("/tmp/tty2.txt", "r") as f:
        #     mergedf.write(f.read().encode('UTF-8'))
        # with open("/tmp/tty1.txt", "r") as f:
        #     mergedf.write(f.read().encode('UTF-8'))

        # mergedf.seek(0)

        # return mergedf, "txt", scan_request
