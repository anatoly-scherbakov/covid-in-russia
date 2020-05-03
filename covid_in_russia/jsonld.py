import dataclasses
from typing import List, Dict, Union

from covid_in_russia.models import Spread


def report_to_jsonld(country_data: List[Spread], regions_data: List[Spread]):
    result = dataclasses.asdict(report)

    result.update({
        '@context': {
            'schema': 'https://schema.org/',
            'iolanta': 'https://iolanta.tech/',
            'rdfs': 'https://www.w3.org/2000/01/rdf-schema#',
            'DBR': 'http://dbpedia.org/resource/',

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
            'rdfs:isDefinedBy': 'DBR:Death',
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
            'rdfs:isDefinedBy': 'DBR:Recovery',
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
            'rdfs:isDefinedBy': 'DBR:People',
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

        'schema:location_iso_code': 'DBR:Russia',
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
            "@version": 1.1,
            'schema': 'https://schema.org/',
            'dcat': 'http://www.w3.org/ns/dcat#',
            'location': {
                '@id': 'dcat:spatial',
                '@type': '@vocab',
                '@context': {
                    '@vocab': 'http://dbpedia.org/resource/',
                }
            },
        },

        '@type': 'dcat:Dataset',
        'location': 'RU',

        'items': list(map(spread_to_jsonld, dataset)),
    }
