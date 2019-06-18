import os

from utils.lambda_decorators import async_handler
from utils.json_serialisation import dumps
import subprocess
import re
from netaddr.core import AddrFormatError
from netaddr import IPNetwork
from shared_task_code.task_queue_consumer import TaskQueueConsumer


# <name> from https://tools.ietf.org/html/rfc952#page-5
ALLOWED_NAME = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)

# from https://tools.ietf.org/html/rfc3696#section-2
ALL_NUMERIC = re.compile(r"[0-9]+$")

# Lifted from https://stackoverflow.com/a/33214423
# Modified to extract compilation of regexes


def is_valid_hostname(hostnameport):
    if hostnameport.count(':') != 1:
        # expect port to be baked into hostname
        return False
    hostname = hostnameport.split(':')[0]
    try:
        # not used but will throw if it is an invalid input
        IPNetwork(hostname)
        return True
    except AddrFormatError:

        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        # the TLD must be not all-numeric
        if ALL_NUMERIC.match(labels[-1]):
            return False

        return all(ALLOWED_NAME.match(label) for label in labels)


def openssl(event, scan, message_id, results_filename, results_dir):
    print('running openssl')
    cmd = f"openssl s_client -showcerts -connect {scan['target']}"
    mergedf = open(results_filename, "w")
    try:

        out = subprocess.check_output(f"echo | {cmd} </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)
        # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later
        mergedf.write(f"scan={dumps(scan)}\n")
        with open("/tmp/tty2.txt", "r") as f:
            mergedf.write(f.read())
        with open("/tmp/tty1.txt", "r") as f:
            mergedf.write(f.read())

    except subprocess.CalledProcessError as e:
        # TODO: put this in DLQ once implemented
        mergedf.write(f"error: {e.output}")
    mergedf.close()


def run_task(event, scan, message_id, results_filename, results_dir):
    if not is_valid_hostname(scan["target"]):
        raise ValueError(
            f"Invalid hostname and/or port for openssl task {scan['target']}")
        return
    print(f"open ssl scan: {scan['target']}")
    openssl(event, scan, message_id, results_filename, results_dir)


@async_handler()
async def submit_scan_task(event, _):
    task_queue_consumer = TaskQueueConsumer(event)
    task_queue_consumer.start(TaskCode=run_task)
