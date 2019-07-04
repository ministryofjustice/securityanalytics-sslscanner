from .ssl_scanner import SslScanner

_ssl_scanner = SslScanner()


def invoke(event, context):
    return _ssl_scanner.invoke(event, context)
