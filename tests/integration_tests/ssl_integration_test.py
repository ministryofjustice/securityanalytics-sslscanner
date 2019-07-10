import pytest
from json import loads
import re
from tests.scan_integration_test_utils.scan_integration_tester import ScanIntegrationTester
from utils.json_serialisation import dumps
import aioboto3

MESSAGE_ID = re.compile(r"^([a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}).*$")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration():
    timeout = 240

    class SslScanIntegrationTester(ScanIntegrationTester):
        def __init__(self, timeout_seconds=120):
            super().__init__(timeout_seconds)
            self.request_msg_id = None
            self._dynamodb_param = f"{self.ssm_source_stage_prefix}/scheduler/dynamodb/resolved_addresses/id"
            self.dynamodb_resource = aioboto3.resource("dynamodb", region_name=self.region)

        def ssm_parameters_to_load(self):
            return super().ssm_parameters_to_load() + [self._dynamodb_param]

        async def send_request(self):
            db_name = self.get_ssm_param(self._dynamodb_param)
            table = self.dynamodb_resource.Table(db_name)

            # so the ssl scan scan be tested we need to give it an entry in dynamo
            # TODO need to stand up our own hosts to scan not use scanme
            respa = await table.update_item(
                Key={
                    "Address": "35.189.73.64",
                    "DnsIngestTime": 1560902409
                },
                UpdateExpression="SET Hosts = :Hosts",
                ExpressionAttributeValues={
                    ":Hosts": set(["scottlogic.com"])
                }
            )

            resp = await self.sqs_client.send_message(
               QueueUrl=self.sqs_input_queue_url,
               # TODO relying on an external resource like this is error prone and unreliable,
               # we should setup a host to scan as part of the test setup instead
               MessageBody=dumps({
                   "Message": dumps({
                       "scan_id": "Scan5",
                       "port_id": "443",
                       "protocol": "tcp",
                       "address": "35.189.73.64",
                       "address_type": "ip",
                       "service": "http",
                       "product": "apache",
                       "version": "0.4",
                   })
               })
            )
            self.request_msg_id = resp["MessageId"]
            print(f"Made request {self.request_msg_id}")

        async def handle_results(self, body):
            result = loads(loads(body)["Message"])
            scan_id = result["scan_id"]

            # TODO need a proper tracing id, this pulling out of the scan of the original
            # input queue message id is not good enough
            original_msg_id_from_scan_id = re.match(MESSAGE_ID, scan_id)[1]
            if original_msg_id_from_scan_id == self.request_msg_id:
                assert True
                print(f"Have received results for initial request with message id {self.request_msg_id}", flush=True)
                await self.cancel_polling()

    await SslScanIntegrationTester(timeout).run_test()
