from .ssl_scanner import SslScanner

_ssl_scanner = None


def invoke(event, context):
    global _ssl_scanner
    if _ssl_scanner is None:
        _ssl_scanner = SslScanner()
    return _ssl_scanner.invoke(event, context)
