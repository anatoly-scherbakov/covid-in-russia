import datetime
import json

from rdflib import Namespace, DCAT, URIRef
from covid_in_russia.jsonld import country_data_to_jsonld
from covid_in_russia import models
from pyld.jsonld import expand


DBR = Namespace('http://dbpedia.org/resource/')


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

    raise Exception(json.dumps(document, indent=2))
