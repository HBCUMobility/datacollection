from warcio.capture_http import capture_http
from pathlib import Path

import hashlib
import json
import os
import requests
import sys

# This script will fetch a URI-Ms in TimeMaps and generate
# ...a WARC from each URI-M.
# Be sure to run ./fetch_timemaps.py to generate TimeMaps


def create_warc_from_timemap(tm_path):
    # This is currently capturing 1 URI-M per WARC, which is not optimal
    f = open(tm_path, 'r')
    while ll := f.readline().strip():
        if ll[0] == '!':  # Exclude CDXJ metadata lines
            continue

        (date14, jsonvals) = ll.split(' ', maxsplit=1)
        uri_m = json.loads(jsonvals)['uri']

        # Call warcio, use hash as filename
        warc_filename = f'{hashlib.sha256(uri_m.encode()).hexdigest()}.warc.gz'
        print(f'Capturing WARC of {uri_m} to {warc_filename}')

        with capture_http(warc_filename):
            requests.get(uri_m)

    f.close()


# Iterate through all of the TimeMaps generated
for root, dirs, files in os.walk(os.path.abspath('./timemaps/')):
    for file in files:
        if file[0] == '.':  # Exclude dotfiles
            continue

        abs_path = os.path.join(root, file)
        tm_size = os.stat(abs_path).st_size

        if tm_size > 0:  # We don't want to parse empty TimeMaps
            print(abs_path)
            create_warc_from_timemap(abs_path)
            sys.exit()  # Premature exit for testing
