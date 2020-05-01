import dataclasses
import io
import json
from datetime import datetime
from typing import NoReturn, List, Dict, Union

import ipfshttpclient
from fire import Fire

from covid_in_russia import web_archive_index, parse, models, enhance
from covid_in_russia.models import Spread

HOMEPAGE = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/information/'


def report_to_jsonld(country_data: List[Spread], regions_data: List[Spread]):
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

        'schema:location_iso_code': 'dbr:Russia',
    })

    result.update(
        reported_time=result['reported_time'].isoformat()
    )

    return result


def spread_to_jsonld(spread: Spread) -> Dict[str, Union[str, int]]:
    datum = dataclasses.asdict(spread)

    datum.update(
        date=spread.date.isoformat(),
        reported_time=spread.reported_time.isoformat(),
        retrieved_time=spread.retrieved_time.isoformat(),
        location=datum.pop('location_iso_code'),
    )

    return datum


def country_data_to_jsonld(dataset: List[Spread]) -> dict:  # type: ignore
    return {
        '@context': {
            'schema': 'https://schema.org/',
            'location': {
                '@id': '',
                '@type': '@id',
            }
        },
        'items': list(map(spread_to_jsonld, dataset)),
    }


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
