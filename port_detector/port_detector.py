from json import loads
from shared_task_code.sns_transformer import FilteringAndTransformingSnsToSnsGlue


# TODO move this out of the ssl scanner and somewhere generic instead
# The port detector listens to the events from nmap scan and uses them to distribute port detection events
# to the sqs input queues of other scans
class PortDetector(FilteringAndTransformingSnsToSnsGlue):
    def __init__(self):
        super().__init__()

    async def handle_incoming_sns_event(self, sns_message):
        msg = loads(sns_message["Message"])["__docs"]
        print(msg)
        if "ports" in msg.keys():
            for port_data in msg["ports"]:
                port_info = {
                    "scan_id": port_data["Data"]["scan_id"],
                    "port_id": port_data["Data"]["port_id"],
                    "protocol": port_data["Data"]["protocol"],
                    "address": port_data["Data"]["address"],
                    "address_type": port_data["Data"]["address_type"],
                    "service": port_data["Data"]["service"] if "service" in port_data["Data"] else "",
                    "product": port_data["Data"]["product"] if "product" in port_data["Data"] else "",
                    "version": port_data["Data"]["version"] if "version" in port_data["Data"] else "",
                }

                print(port_info)
                await self.forward_message(port_info, port_info)
