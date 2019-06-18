import os
from utils.lambda_decorators import async_handler
import re
from utils.scan_results import ResultsContext
from shared_task_code.results_parser import ResultsParser


def process_results(results_context, body, **kwargs):
    print(f"body length is {len(body)}")
    chain = {'records': []}
    is_root_ca = True
    if len(body) > 0 and ('error' in body[0]):
        results_context.push_context({"ssl_chain": "No SSL"})
        results_context.post_results("data", {}, include_summaries=True)
        results_context.pop_context()
    else:
        for line in body:
            if 'depth' in line:
                record = {}
                params = re.split(r',\s+(?=(?:(?:[^"]*"){2})*[^"]*$)', line.split(' ', 1)[1].replace('\n', ''))
                record['depth'] = int(line.split('depth=')[1].split(' ')[0])
                record['rootCA'] = is_root_ca
                # Top of returned values is always root, first time round the loop it'll be True
                is_root_ca = False
                for param in params:
                    psplit = param.split(' = ')
                    record[psplit[0]] = psplit[1]
                chain['records'].append(record)
            if 'DONE' in line:
                break
        results_context.push_context({"ssl_chain": "Valid"})

        # TODO store start_time correctly
        # TODO end_time will be correct once the scheduler is in place to change the key (currently end_time is used)

        for cert in chain['records']:
            results_context.push_context({"depth": f"{cert['depth']}", "root_ca": f"{cert['rootCA']}"})
            results = {}
            for element in cert:
                if (element is not "depth") and (element is not "rootCA"):
                    results[element] = cert[element]
            results_context.post_results("data", results, include_summaries=True)
            results_context.pop_context()


@async_handler()
async def parse_results(event, _):
    results_parser = ResultsParser(event)
    results_parser.start(IterateResults=process_results)
