from json import loads
from shared_task_code.sns_listener import FilteringAndTransformingSnsToSnsGlue


# The port detector listens to the events from nmap scan and uses them to distribute port detection events
# to the sqs input queues of other scans
class PortDetector(FilteringAndTransformingSnsToSnsGlue):
    def __init__(self):
        FilteringAndTransformingSnsToSnsGlue.__init__(self, [])

    async def handle_incoming_sns_event(self, sns_message):
        msg = loads(sns_message["Message"])
        if "ports" in msg.keys():
            for port_data in msg["ports"]:
                port_info = {
                    "scan_id": msg["scan_id"],
                    "port_id": port_data["port_id"],
                    "protocol": port_data["protocol"],
                    "address": msg["address"],
                    "address_type": msg["address_type"],
                    "service": port_data["service"] if "service" in port_data else None,
                    "product": port_data["product"] if "product" in port_data else None,
                    "version": port_data["version"] if "version" in port_data else None,
                }
                print(port_info)
                await self.forward_message(port_info, port_info)
