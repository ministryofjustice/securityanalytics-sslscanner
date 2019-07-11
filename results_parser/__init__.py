from .results_parser import SslResultsParser

_results_parser = None


def invoke(event, context):
    global _results_parser
    if _results_parser is None:
        _results_parser = SslResultsParser()
    return _results_parser.invoke(event, context)
