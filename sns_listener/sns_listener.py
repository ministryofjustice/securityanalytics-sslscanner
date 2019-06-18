from utils.lambda_decorators import async_handler
from shared_task_code.sns_listener import SNSListener
from json import loads


def check_and_queue(event, sns_rec, sns_listener):
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
                sns_listener.sendToSQS(scan)


@async_handler()
async def check_event(event, _):
    sns_listener = SNSListener(event)
    sns_listener.start(PassToQueue=check_and_queue)
