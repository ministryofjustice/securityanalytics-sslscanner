from unittest import mock
import pytest
import os
import itertools
from test_utils.test_utils import resetting_mocks, serialise_mocks


TEST_ENV = {
    'REGION': 'eu-west-wood',
    'STAGE': 'door',
    'APP_NAME': 'me-once',
    'TASK_NAME': 'me-twice',
}

with mock.patch.dict(os.environ, TEST_ENV), \
        mock.patch('boto3.client') as boto_client, \
        mock.patch('utils.json_serialisation.stringify_all'):
    # ensure each client is a different mock
    boto_client.side_effect = (mock.MagicMock() for _ in itertools.count())
    from task_queue_consumer import task_queue_consumer


@mock.patch.dict(os.environ, TEST_ENV)
def ssm_return_vals(using_private):
    stage = os.environ["STAGE"]
    app_name = os.environ["APP_NAME"]
    task_name = os.environ["TASK_NAME"]
    ssm_prefix = f"/{app_name}/{stage}"
    return {
        'Parameters': [
            {"Name": f"{ssm_prefix}/tasks/{task_name}/s3/results/id", "Value": "bid"}
        ]
    }


@pytest.mark.unit
@serialise_mocks()
@resetting_mocks(task_queue_consumer.ssm_client.get_parameters)
def test_task_queue_consumer_valid_host_port():
    task_queue_consumer.ssm_client.get_parameters.return_value = ssm_return_vals(True)

    # we just want to check the input
    task_queue_consumer.openssl = mock.Mock()
    task_queue_consumer.submit_scan_task(
        {"Records":
         [{"body": '{"target":"mywebsitetest.com:443", "address":"mywebsitetest.com", "address_type":"ipv4", "scan_end_time":"May 28th 2019, 00:00:00.000"}', "messageId": "13"}]},
        mock.MagicMock())
    expected = ({"Records": [{"body":  '{"target":"mywebsitetest.com:443", "address":"mywebsitetest.com", "address_type":"ipv4", "scan_end_time":"May 28th 2019, 00:00:00.000"}', "messageId": "13"}],
                 "ssm_params": {"/me-once/door/tasks/me-twice/s3/results/id": "bid"}},
                {"target": "mywebsitetest.com:443", "address": "mywebsitetest.com", "address_type": "ipv4", "scan_end_time": "May 28th 2019, 00:00:00.000"}, "13")
    task_queue_consumer.openssl.assert_called_once_with(*expected)


@pytest.mark.unit
@serialise_mocks()
@resetting_mocks(task_queue_consumer.ssm_client.get_parameters)
def test_task_queue_consumer_invalid_host_port():
    task_queue_consumer.ssm_client.get_parameters.return_value = ssm_return_vals(True)

    # we just want to check the input
    task_queue_consumer.openssl = mock.Mock()
    with pytest.raises(ValueError):
        task_queue_consumer.submit_scan_task(
            {"Records": [{"body": '{"target":"invalid_underscore.com:443", "address":"invalid_underscore.com", "address_type":"ipv4", "scan_end_time":"May 28th 2019, 00:00:00.000"}', "messageId": "13"}]},
            mock.MagicMock())


@pytest.mark.unit
@serialise_mocks()
@resetting_mocks(task_queue_consumer.ssm_client.get_parameters)
def test_task_queue_consumer_no_port():
    task_queue_consumer.ssm_client.get_parameters.return_value = ssm_return_vals(True)

    # we just want to check the input
    task_queue_consumer.openssl = mock.Mock()
    with pytest.raises(ValueError):
        task_queue_consumer.submit_scan_task(
            {"Records": [{"body":  '{"target":"mywebsitetest.com", "address":"mywebsitetest.com", "address_type":"ipv4", "scan_end_time":"May 28th 2019, 00:00:00.000"}', "messageId": "13"}]},
            mock.MagicMock())
