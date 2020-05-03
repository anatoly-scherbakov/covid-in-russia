import dataclasses
from typing import List, Dict, Union

from covid_in_russia.models import Spread


def spread_to_jsonld(spread: Spread) -> Dict[str, Union[str, int]]:
    """Convert a data point into JSON-LD dict."""
    datum = dataclasses.asdict(spread)

    datum.update(
        date=spread.date.isoformat(),
        reported_time=spread.reported_time.isoformat(),
        retrieved_time=spread.retrieved_time.isoformat(),
        location=datum.pop('location_iso_code'),
    )

    return datum


def graph() -> List[dict]:  # type: ignore
    """@graph definition."""
    return [{
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
    }]


def context() -> dict:  # type: ignore
    return {
        "@version": 1.1,

        'schema': 'https://schema.org/',
        'dct': 'http://purl.org/dc/terms/',
        'dcat': 'http://www.w3.org/ns/dcat#',
        'rdfs': 'https://www.w3.org/2000/01/rdf-schema#',

        'iolanta': 'https://iolanta.tech/',
        'table': 'https://iolanta.tech/table/',

        'location': {
            '@id': 'dcat:spatial',
            '@type': '@vocab',
            '@context': {
                '@vocab': 'http://dbpedia.org/resource/',
            }
        },

        # Can't find anything better at this point.
        'items': 'dct:hasPart',

        'date': 'schema:dateCreated',
        'reported_time': 'schema:datePublished',
        'retrieved_time': 'schema:dateReceived',

        'total': {
            '@id': '_:total',
            '@type': 'xsd:integer',
        },
        'deceased': {
            '@id': '_:deceased',
            '@type': 'xsd:integer',
        },
        'recovered': {
            '@id': '_:recovered',
            '@type': 'xsd:integer',
        },
        'source': {
            '@id': 'schema:isBasedOn',
            '@type': '@id',
        },

        'table:columns': {
            '@type': '@id',
        },

        'table:row': {
            '@type': '@id',
        },
    }


def iolanta() -> dict:  # type: ignore
    return {
        '@type': 'table:Table',
        'table:row': 'dct:hasPart',
        'table:columns': [
            'dcat:spatial',

            '_:total',
            '_:recovered',
            '_:deceased',

            'schema:dateCreated',
        ],
    }


def country_data_to_jsonld(dataset: List[Spread]) -> dict:  # type: ignore
    """Formulate dataset for Russia as a whole in JSON-LD."""
    return {
        '@context': context(),

        '@graph': graph(),
        '@type': 'dcat:Dataset',

        'location': 'RU',
        'rdfs:label': [{
            '@language': 'ru',
            '@value': 'Заболеваемость COVID-19 в России',
        }, {
            '@language': 'en',
            '@value': 'COVID-19 spread in Russia',
        }],

        'iolanta:app': iolanta(),

        'items': list(map(spread_to_jsonld, dataset)),
    }
