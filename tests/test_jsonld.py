import datetime
import json
import operator

from pyld.jsonld import expand
from rdflib import Namespace, DCTERMS, SDO, DCAT

from covid_in_russia import models
from covid_in_russia.jsonld import country_data_to_jsonld

DBR = Namespace('http://dbpedia.org/resource/')
IO = Namespace('https://iolanta.tech/')
TAB = Namespace('https://iolanta.tech/table/')


def test_dataset_location_expanded():
    document, = expand(country_data_to_jsonld([]))
    assert document[
        str(DCAT.spatial)
    ][0]['@id'] == str(DBR.RU)


def test_item():
    document, = expand(country_data_to_jsonld(dataset=[models.Spread(
        date=datetime.date(2020, 5, 3),
        reported_time=datetime.datetime(2020, 5, 3, 10, 30),
        retrieved_time=datetime.datetime(2020, 5, 3, 18, 39),
        location_iso_code='RU',
        total=5,
        recovered=5,
        deceased=0,
        source='my-imagination',
    )]))

    spread, = document[str(DCTERMS.hasPart)]

    assert spread[str(DCAT.spatial)][0]['@id'] == str(DBR.RU)
    assert spread[str(SDO.dateCreated)][0]['@value'] == '2020-05-03'
    assert spread[str(SDO.datePublished)][0]['@value'] == '2020-05-03T10:30:00'
    assert spread[str(SDO.dateReceived)][0]['@value'] == '2020-05-03T18:39:00'

    assert spread['_:total'][0]['@value'] == 5
    assert spread['_:deceased'][0]['@value'] == 0
    assert spread['_:recovered'][0]['@value'] == 5


def test_iolanta_app():
    document, = expand(country_data_to_jsonld([]))

    app = document[str(IO.app)][0]
    assert app['@type'][0] == str(TAB.Table)
    assert list(map(
        operator.itemgetter('@id'),
        app[str(TAB.columns)],
    )) == [
        str(DCAT.spatial),
        '_:total',
        '_:recovered',
        '_:deceased',
        str(SDO.dateCreated),
    ]
    assert app[str(TAB.row)][0]['@id'] == str(DCTERMS.hasPart)
