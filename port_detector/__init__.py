from .port_detector import PortDetector

_port_detector = PortDetector()


def invoke(event, context):
    return _port_detector.invoke(event, context)
