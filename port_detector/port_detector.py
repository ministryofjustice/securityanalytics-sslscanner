from json import loads
from shared_task_code.sns_transformer import FilteringAndTransformingSnsToSnsGlue


# The port detector listens to the events from nmap scan and uses them to distribute port detection events
# to the sqs input queues of other scans
class PortDetector(FilteringAndTransformingSnsToSnsGlue):
    def __init__(self):
        FilteringAndTransformingSnsToSnsGlue.__init__(self, [])

    # def check_and_queue(event, sns_rec, sns_listener):
    #     msg = loads(sns_rec["Message"])["__docs"]
    #     if "ports" in msg.keys():
    #         for port_data in msg["ports"]:
    #             if port_data["Data"]["port_id"] == "443" or port_data["Data"]["service"] == "https":
    #                 scan = {"target": f'{port_data["Data"]["address"]}:{port_data["Data"]["port_id"]}',
    #                         "address": port_data["Data"]["address"],
    #                         "address_type": port_data["Data"]["address_type"]}
    #                 sns_listener.sendToSQS(scan)

    async def handle_incoming_sns_event(self, sns_message):
        msg = loads(sns_message["Message"])["__docs"]
        print(msg)
        if "ports" in msg.keys():
            for port_data in msg["ports"]:
                port_info = {

                    "port_id": port_data["Data"]["port_id"],
                    "protocol": port_data["Data"]["protocol"],
                    "address": port_data["Data"]["address"],
                    "address_type": port_data["Data"]["address_type"],
                    "service": port_data["Data"]["service"] if "service" in port_data["Data"] else "",
                    "product": port_data["Data"]["product"] if "product" in port_data["Data"] else "",
                    "version": port_data["Data"]["version"] if "version" in port_data["Data"] else "",
                }
                # "scan_id": msg["scan_id"],
                # "address": msg["address"],
                # "address_type": msg["address_type"],
                print(port_info)
                await self.forward_message(port_info, port_info)
