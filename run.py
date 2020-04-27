import dataclasses
import io
import json
from typing import NoReturn
from fire import Fire
import ipfshttpclient
from covid_in_russia import web_archive_index, parse, models, enhance
from pyld import jsonld


HOMEPAGE = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/'


def report_to_jsonld(report: models.Report):
    result = dataclasses.asdict(report)

    result.update({
        '@context': {
            'index_cid': {
                '@id': 'https://schema.org/isBasedOnUrl',
                '@type': '@id',
            },
            'page_cid': {
                '@id': 'https://schema.org/isBasedOnUrl',
                '@type': '@id',
            },
            'per_region': {
                '@id': 'https://schema.org/ItemList',
                '@container': '@list',
            },
            'region': {
                '@id': 'https://schema.org/Place',
                '@type': '@id',
            },
            'deceased': {
                '@id': 'http://dbpedia.org/page/Death',
                '@type': 'xsd:integer'
            },
            'recovered': {
                '@id': 'http://dbpedia.org/page/Recovery',
                '@type': 'xsd:integer'
            },
            'total': {
                '@id': 'http://dbpedia.org/page/People',
                '@type': 'xsd:integer'
            }
        }
    })

    result = jsonld.expand(result)
    return result


def main(index_file_cid: str) -> NoReturn:
    with ipfshttpclient.connect() as client:
        index_content = client.cat(index_file_cid).decode('utf-8')

    index = web_archive_index.WebArchiveIndex.from_string(index_content)

    record = index.find_by_original_uri(HOMEPAGE)
    html_page_cid = record.data['locator'].split('/')[-1]

    with ipfshttpclient.connect() as client:
        html_content = client.cat(html_page_cid).decode('utf-8')

    report = parse.parse_html(html_content)
    report = parse.calculate_totals(report)
    report = enhance.add_regions(report)

    report = dataclasses.replace(
        report,
        index_cid=f'ipfs://{index_file_cid}',
        page_cid=f'ipfs://{html_page_cid}',
    )

    json_report = report_to_jsonld(report)

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
