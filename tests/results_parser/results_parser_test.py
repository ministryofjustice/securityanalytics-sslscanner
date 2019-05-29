from unittest import mock
import pytest
import os
import json
import itertools
from test_utils.test_utils import resetting_mocks, serialise_mocks
from utils.json_serialisation import dumps
from botocore.response import StreamingBody

TEST_ENV = {
    "REGION": "eu-west-wood",
    "STAGE": "door",
    "APP_NAME": "me-once",
    "TASK_NAME": "me-twice",
}
TEST_DIR = "./tests/results_parser/"

with mock.patch.dict(os.environ, TEST_ENV), \
    mock.patch("boto3.client") as boto_client, \
        mock.patch("utils.json_serialisation.stringify_all"):
    # ensure each client is a different mock
    boto_client.side_effect = (mock.MagicMock() for _ in itertools.count())
    from results_parser import results_parser


@mock.patch.dict(os.environ, TEST_ENV)
def ssm_return_vals():
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"
    return {
        "Parameters": [
            {"Name": f"{ssm_prefix}/tasks/{task_name}/results/arn", "Value": "test_topic"}
        ]
    }


def expected_pub(doc_type, doc):
    return {
        "TopicArn": "test_topic",
        "Subject": doc_type,
        "Message": dumps(doc)
    }


@pytest.mark.unit
@serialise_mocks()
@resetting_mocks(
    results_parser.sns_client,
    results_parser.s3_client,
    results_parser.ssm_client
)
def test_parses_hosts_and_ports():
    results_parser.ssm_client.get_parameters.return_value = ssm_return_vals()

    # load sample results file and make mock return it
    sample_file_name = f"{TEST_DIR}053dacb6-91bf-4aaa-8790-8224d65d5d88-2019-05-28T101309-ssl.txt.tar.gz"
    with open(sample_file_name, "rb") as sample_data:
        results_parser.s3_client.get_object.return_value = {
            "Body": StreamingBody(sample_data, os.stat(sample_file_name).st_size)
        }

        results_parser.parse_results({
            "Records": [
                {"s3": {
                    "bucket": {"name": "test_bucket"},
                    # Please note that the / characters in the key are replaced with %2F, the key is
                    # urlencoded
                    "object": {"key": "053dacb6-91bf-4aaa-8790-8224d65d5d88-2019-05-28T101309-ssl.txt.tar.gz"}
                }}
            ]
        }, mock.MagicMock())
        results_parser.sns_client.publish.call_count == 3


def test_parses_quotes_in_ca():
    results_parser.ssm_client.get_parameters.return_value = ssm_return_vals()

    # load sample results file and make mock return it
    sample_file_name = f"{TEST_DIR}f530f0c4-64ff-41d4-8bcd-012d2f16d161-2019-05-29T130337-ssl.txt.tar.gz"
    with open(sample_file_name, "rb") as sample_data:
        results_parser.s3_client.get_object.return_value = {
            "Body": StreamingBody(sample_data, os.stat(sample_file_name).st_size)
        }

        results_parser.parse_results({
            "Records": [
                {"s3": {
                    "bucket": {"name": "test_bucket"},
                    # Please note that the / characters in the key are replaced with %2F, the key is
                    # urlencoded
                    "object": {"key": "f530f0c4-64ff-41d4-8bcd-012d2f16d161-2019-05-29T130337-ssl.txt.tar.gz"}
                }}
            ]
        }, mock.MagicMock())
        results_parser.sns_client.publish.call_count == 4
