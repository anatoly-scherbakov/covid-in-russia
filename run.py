import dataclasses
import io
import json
from typing import NoReturn

import ipfshttpclient
from fire import Fire

from covid_in_russia import web_archive_index, parse, models, enhance

HOMEPAGE = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/'


def report_to_jsonld(report: models.Report):
    result = dataclasses.asdict(report)

    result.update({
        '@context': {
            'schema': 'https://schema.org/',
            'iolanta': 'https://iolanta.tech/',
            'rdfs': 'https://www.w3.org/2000/01/rdf-schema#',
            'dbr': 'http://dbpedia.org/resource/',

            'index_cid': {
                '@id': 'https://schema.org/isBasedOnUrl',
                '@type': '@id',
            },
            'page_cid': {
                '@id': 'https://schema.org/isBasedOnUrl',
                '@type': '@id',
            },
            'per_region': 'rdfs:member',

            'region': '_:russian_region',
            'deceased': '_:deceased',
            'recovered': '_:recovered',
            'total': '_:total',
            'reported_time': 'schema:datePublished',
        },

        '@graph': [{
            '@id': '_:russian_region',
            'rdfs:subClassOf': 'schema:Place',
            '@type': '@id',
            'rdfs:label': [{
                '@value': 'Регион',
                '@language': 'ru',
            }, {
                '@value': 'Region',
                '@language': 'en',
            }]
        }, {
            '@id': '_:deceased',
            '@type': 'rdfs:Property',
            'rdfs:isDefinedBy': 'dbr:Death',
            'rdfs:domain': 'xsd:integer',
            'rdfs:label': [{
                '@value': 'Умерло',
                '@language': 'ru',
            }, {
                '@value': 'Deceased',
                '@language': 'en',
            }]
        }, {
            '@id': '_:recovered',
            '@type': 'rdfs:Property',
            'rdfs:isDefinedBy': 'dbr:Recovery',
            'rdfs:domain': 'xsd:integer',
            'rdfs:label': [{
                '@value': 'Человек выздоровело',
                '@language': 'ru'
            }, {
                '@value': 'Recovered',
                '@language': 'en',
            }]
        }, {
            '@id': '_:total',
            '@type': 'rdfs:Property',
            'rdfs:isDefinedBy': 'dbr:People',
            'rdfs:domain': 'xsd:integer',
            'rdfs:label': [{
                '@value': 'Всего случаев',
                '@language': 'ru'
            }, {
                '@value': 'Confirmed Cases',
                '@language': 'en',
            }]
        }],

        'iolanta:app': [{
            '@id': 'iolanta:table',
        }, {
            '@id': 'iolanta:map',
        }],

        '@id': '_:dataset',
        'rdfs:label': [{
            '@language': 'ru',
            '@value': 'Заболеваемость COVID-19 по регионам России',
        }, {
            '@language': 'en',
            '@value': 'COVID-19 morbidity by Russia regions',
        }],

        'schema:location': 'dbr:Russia',
    })

    result.update(
        reported_time=result['reported_time'].isoformat()
    )

    return result


def main(index_file_cid: str) -> NoReturn:
    with ipfshttpclient.connect() as client:
        index_content = client.cat(index_file_cid).decode('utf-8')

    index = web_archive_index.WebArchiveIndex.from_string(index_content)

    record = index.find_by_original_uri(HOMEPAGE)
    html_page_cid = record.data['locator'].split('/')[-1]

    with ipfshttpclient.connect() as client:
        html_content = client.cat(html_page_cid).decode('utf-8')

    raise Exception(html_content)

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
