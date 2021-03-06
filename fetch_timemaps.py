#!/usr/bin/env python3

'''% for x in $(ls *.xlsx); do x1=${x%".xlsx"};
 in2csv $x > $x1.csv; echo "$x1.csv done."; done'''
import glob
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

import aiohttp
import asyncio

from warcio.capture_http import capture_http
import requests  # requests must be imported after capture_http for warcio
import validators

# NOTE: set up your own, local MemGator instance for faster, more reliable results.
# > see https://github.com/oduwsdl/memgator
memento_aggregator = 'http://localhost:1208'
# memento_aggregator = 'https://aggregator.matkelly.com'

# JSON and Link (rfc8288) TimeMaps are also available via MemGator
timemap_uri = f'{memento_aggregator}/timemap/cdxj/'
url_field_location = 1  # 0-based, a better approach is needed for extraction

data_files = glob.glob("src_data/*.csv")

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)


def make_filename_from_uri(uri_r: str) -> str:
    url = urlparse(uri_r)
    path = f'timemaps/{url.hostname}'
    os.makedirs(path, exist_ok=True)
    filename_hash = hashlib.sha256(uri_r.encode()).hexdigest()
    return f'{path}/{filename_hash}.tm.txt'


def fabricate_tm_for_no_mementos(uri_r: str) -> str:
    # nopep8
    return (
        '!context ["https://oduwsdl.github.io/contexts/memento"]\n'
        f'!id {{"uri": "http://localhost:1208/timemap/cdxj/{uri_r}https://www.coppin.edu/son"}}\n'
        '!keys ["memento_datetime_YYYYMMDDhhmmss"]\n'
        f'!meta {{"original_uri": "{uri_r}"}}\n'
        f'!meta {{"timegate_uri": "http://localhost:1208/timegate/{uri_r}"}}\n'
        '!meta {"note": "This TimeMap was fabricated for a URI-R with no mementos"}\n'
    )


async def fetch_timemap(uri_r: str, session: aiohttp.ClientSession) -> str:
    uri_t = f'{timemap_uri}{uri_r}'

    response = await session.request(method='GET', url=uri_t)

    # Transform URL to filename, retain TimeMap on file system
    timemap_file_path = make_filename_from_uri(uri_r)

    logging.info(f'Writing {timemap_file_path}')

    # If there are no mementos in the TimeMap, write an empty file to disk
    if response.status == 404:
        with open(timemap_file_path, 'w+') as f:
            f.write(fabricate_tm_for_no_mementos(uri_r))
        return str(Path(timemap_file_path).resolve())

    # If a TimeMap is returned, write it to disk
    with open(timemap_file_path, 'wb') as f:
        while True:
            chunk = await response.content.read()
            if not chunk:
                break
            f.write(chunk)

    # Return absolute path to TimeMap file
    return str(Path(timemap_file_path).resolve())


def extract_original_uris(filename: str) -> list:
    with open(filename) as f:
        csv = f.read()

    csv_rows = csv.split('\n')

    uri_rs = list()
    for csv_row in csv_rows:
        csv_fields = csv_row.split(',')

        if len(csv_fields) < 2 or not validators.url(csv_fields[url_field_location]):
            continue
        uri_rs.append(csv_fields[1])

    return uri_rs


def print_memento_metadata(filename: str):
    uri_r = ''
    m_count = 0  # number of mementos
    first_date = 0  # Date of oldest memento
    last_date = 0  # Date of most recent memento
    with open(filename, 'r') as f:
        for line in f:
            date14, json_data = line.split(' ', maxsplit=1)
            j = json.loads(json_data)

            # Disregard metadata lines, content headers, etc.
            if not date14.isdigit():
                if date14 == '!id':  # Get URI-R to TimeMap
                    uri_r = j['uri']

            if 'rel' not in j:  # Header line
                continue

            if 'memento' in j['rel']:
                m_count += 1
            if 'first' in j['rel']:
                first_date = date14
            if 'last' in j['rel']:
                last_date = date14

    logging.info((
        f'{m_count} captures found for {uri_r}\n'
        f'* First: {first_date}\n* Last: {last_date}'))

    # with capture_http('howard.warc.gz'):
    #    requests.get('https://put.the.urim.here')


async def main():
    # From CSVs, transformed from XLSX, see top of src for cmd
    uri_rs = []
    for data_file in data_files:
        uri_rs = extract_original_uris(data_file)

        simultaneous_connections = 2
        connector = aiohttp.TCPConnector(limit=simultaneous_connections)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []

            # Queue TimeMap fetching tasks
            for uri_r in uri_rs:
                tasks.append(fetch_timemap(uri_r=uri_r, session=session))

            await asyncio.gather(*tasks)

    for uri_r in uri_rs:
        filename = make_filename_from_uri(uri_r)
        print_memento_metadata(filename)

if __name__ == '__main__':
    asyncio.run(main())
