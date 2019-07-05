import os
from utils.lambda_decorators import async_handler
import re
from utils.scan_results import ResultsContext
from shared_task_code.base_results_parser import ResultsParser


class SslResultsParser(ResultsParser):

    def __init__(self):
        ResultsParser.__init__(self, [])

    async def parse_results(self, results_file_name, results_doc, meta_data):
        print(meta_data)
        scan_id = os.path.splitext(results_file_name)[0]
        start_time = meta_data["scan_start_time"]
        end_time = meta_data["scan_end_time"]

        non_temporal_key = {
            "address": meta_data["address"],
            "address_type": meta_data["address_type"]
        }

        results_context = self.create_results_context(non_temporal_key, scan_id, start_time, end_time)

        chain = {'records': []}
        body = results_doc.read().decode('utf-8').split('\n')
        is_root_ca = True
        if len(body) > 0 and ('error' in body[0]):
            results_context.push_context({"ssl_chain": "No SSL", "hostname": meta_data["target"]})
            results_context.post_results("data", {}, include_summaries=True)
            results_context.publish_results()
            results_context.pop_context()
        else:
            record = {}
            verify_code = ''
            verify_reason = ''
            print(body)
            for line in body:
                if 'depth' in line:
                    if record != {}:
                        chain['records'].append(record)
                        record = {}
                    params = re.split(r',\s+(?=(?:(?:[^"]*"){2})*[^"]*$)', line.split(' ', 1)[1].replace('\n', ''))
                    record['depth'] = line.split('depth=')[1].split(' ')[0]
                    record['rootCA'] = is_root_ca
                    # Top of returned values is always root, first time round the loop it'll be True
                    is_root_ca = False
                    for param in params:
                        psplit = param.split(' = ')
                        record[psplit[0]] = psplit[1]
                if 'verify error' in line and record != {}:
                    verify = line.split(':', 3)
                    record['verify error code'] = verify[1]
                    record['verify error msg'] = verify[2]
                    chain['records'].append(record)
                    record = {}
                if 'Verify return code:' in line:
                    verify = line.split('Verify return code: ', 1)[1].split(' ', 1)
                    verify_code = verify[0]
                    verify_reason = verify[1][1: -1]
                    break
            if record != {}:
                chain['records'].append(record)
                record = {}
            results_context.push_context(
                {"ssl_chain": "Valid", "hostname": meta_data["target"], "verify_code": verify_code, "verify_reason": verify_reason})
            print("CHAIN")
            print(chain)
            for cert in chain['records']:
                results_context.push_context({"depth": f"{cert['depth']}", "root_ca": f"{cert['rootCA']}"})
                # results_context.push_context(cert)
                results = {}
                for element in cert:
                    if (element is not "depth") and (element is not "rootCA"):
                        results[element] = cert[element]
                results_context.post_results("data", results, include_summaries=True)
                await results_context.publish_results()
                results_context.pop_context()


@async_handler()
async def parse_results(event, _):
    results_parser = ResultsParser(event)
    results_parser.start(IterateResults=process_results)
