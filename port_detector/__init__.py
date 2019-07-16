from .port_detector import PortDetector

_port_detector = None


def invoke(event, context):
    global _port_detector
    if _port_detector is None:
        _port_detector = PortDetector()
    return _port_detector.invoke(event, context)
