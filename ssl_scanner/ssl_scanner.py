import io
import subprocess
from shared_task_code.lambda_scanner import LambdaScanner
from .host_validation import is_valid_hostname
from json import loads


class SslScanner(LambdaScanner):
    def __init__(self):
        super().__init__([])

    async def scan(self, scan_request_id, scan_request):
        scan_request = loads(scan_request)
        target = scan_request["target"]

        if not is_valid_hostname(target):
            raise ValueError(
                f"Invalid hostname and/or port for openssl task {target}")

        print(f"open ssl scan: {scan_request['target']} for request id {scan_request_id}")
        print('running openssl')
        cmd = f"openssl s_client -showcerts -connect {target}"
        mergedf = io.BytesIO()

        try:
            out = subprocess.check_output(f"echo | {cmd} </dev/null 1>/tmp/tty1.txt 2>/tmp/tty2.txt", shell=True)
            # openssl outputs on two tty streams, so merge the two together and put in S3 for processing later

        except subprocess.CalledProcessError as e:
            # openssl will generate an error if there's a problem in the chain - just get the output and do something with it
            pass

        with open("/tmp/tty2.txt", "r") as f:
            mergedf.write(f.read().encode('UTF-8'))
        with open("/tmp/tty1.txt", "r") as f:
            mergedf.write(f.read().encode('UTF-8'))

        mergedf.seek(0)

        return mergedf, "txt", scan_request
