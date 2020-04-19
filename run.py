import dataclasses
import json
from typing import NoReturn
from fire import Fire
import ipfshttpclient
from covid_in_russia import web_archive_index, parse


HOMEPAGE = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/'


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

    report = dataclasses.replace(
        report,
        index_cid=index_file_cid,
        page_cid=html_page_cid,
    )

    json_report = dataclasses.asdict(report)

    with ipfshttpclient.connect() as client:
        json_cid = client.add_json(json_report)

    print(json_cid)


if __name__ == '__main__':
    Fire(main)
