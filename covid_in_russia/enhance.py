import dataclasses
from typing import Dict

from SPARQLWrapper import SPARQLWrapper, JSON

from covid_in_russia import models

URL = 'http://dbpedia.org/sparql'


QUERY = '''SELECT ?name ?region WHERE {
  ?region a dbo:AdministrativeRegion .
  ?region dbo:country DBR:Russia .

  {
    ?region rdfs:label ?name .
    FILTER(lang(?name) = 'ru')
  } UNION {
    ?region dbp:ruName ?name .
  }
}'''


HARDCODED_MAPPING = {
    'Республика Чувашия': 'http://dbpedia.org/resource/Chuvashia',
    'Ханты-Мансийский АО': (
        'http://dbpedia.org/resource/Khanty-Mansi_Autonomous_Okrug'
    ),
    'Республика Саха (Якутия)': 'http://dbpedia.org/resource/Sakha_Republic',
    'Севастополь': 'http://dbpedia.org/resource/Sevastopol',
}


def get_region_map() -> Dict[str, str]:
    sparql = SPARQLWrapper(URL)
    sparql.setQuery(QUERY)
    sparql.setReturnFormat(JSON)
    bindings = sparql.query().convert()['results']['bindings']

    mapping = {
        item['name']['value']: item['region']['value']
        for item in bindings
    }

    mapping.update(HARDCODED_MAPPING)

    return mapping


def add_regions(report: models.Report) -> models.Report:
    region_map = get_region_map()

    return dataclasses.replace(
        report,
        per_region=[dataclasses.replace(
            record,
            region=region_map[record.region]
        ) for record in report.per_region]
    )
