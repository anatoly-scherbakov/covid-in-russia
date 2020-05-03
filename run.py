import io
import json
from typing import NoReturn

import ipfshttpclient
import pyld
from fire import Fire

from covid_in_russia import web_archive_index, parse
from covid_in_russia.jsonld import country_data_to_jsonld

HOMEPAGE = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/information/'


def main(index_file_cid: str) -> NoReturn:
    with ipfshttpclient.connect() as client:
        index_content = client.cat(index_file_cid).decode('utf-8')

    index = web_archive_index.WebArchiveIndex.from_string(index_content)

    record = index.find_by_original_uri(HOMEPAGE)

    assert record is not None

    html_page_cid = record.data['locator'].split('/')[-1]

    with ipfshttpclient.connect() as client:
        html_content = client.cat(html_page_cid).decode('utf-8')

    country_data, regions_data = parse.parse_html(
        html_content,
        retrieved_time=record.retrieved_time,
        source_url=f'ipfs://{html_page_cid}',
    )

    json_report = country_data_to_jsonld(country_data)

    json_report = pyld.jsonld.expand(json_report)

    print(json.dumps(json_report, indent=2, ensure_ascii=False))

    # json_cid = store_to_ipfs(html_page_cid, index_file_cid, json_report)

    # print(json_cid)


def store_to_ipfs(html_page_cid, index_file_cid, json_report):
    with ipfshttpclient.connect() as client:
        json_cid = client.object.put(io.BytesIO(json.dumps({
            'Data': json.dumps(json_report),
            'Links': [{
                'Hash': html_page_cid,
                'Name': 'derivedFrom',
            }, {
                'Hash': index_file_cid,
                'Name': 'derivedFrom',
            }]
        }).encode('utf-8')))
    return json_cid


if __name__ == '__main__':
    Fire(main)
