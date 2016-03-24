#!/usr/bin/env python

import csv
import os
import requests
import sys
import re

#GEOCODE_URL = 'http://who.owns.nyc/geoclient/address.json'
GEOCODE_URL = 'https://api.cityofnewyork.us/geoclient/v1/address.json'
APP_ID = 'aeb3d5cf'
APP_KEY = '8877140c9a6b5c567c27ab7d82260bbf'
HEADERS = [
    'house_number',
    'street',
    'borough',
    'pound_code',
    'star_code',
    'bbl',
    'zip_code',
    'longitude',
    'latitude',
    'error'
]

#?houseNumber=993&street=carroll+st&borough=3


def geocode(housenum, street, borough):
    return requests.get(GEOCODE_URL, params={
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'houseNumber': housenum,
        'street': street,
        'borough': borough
    }).json()


def process_txt(path, output):
    borough = path.split(os.path.sep)[1].replace('_', ' ')
    with open(path) as infile:
        for rownum, line in enumerate(infile):
            parts = line.split()
            if len(parts) < 2:
                continue
            #time.sleep(0.5)
            housenum = parts[0]
            if housenum.lower() in ('bronx', 'kings', 'new', 'queens', 'richmond'):
                continue
            street = ' '.join(parts[1:]).decode('utf8')
            last_chars = street[-2:]
            pound_code = False
            star_code = False
            if '*' in last_chars:
                star_code = True
                street = re.sub('\*$', '', street)
            if '#' in last_chars:
                pound_code = True
                street = re.sub('#$', '', street)
            if u"\u2018" in last_chars:
                star_code = True
                street = re.sub(u"\u2018$", '', street)
            street = re.sub(' S1$', ' St', street)
            street = re.sub(' SI$', ' St', street)
            street = re.sub(' 51$', ' St', street)
            street = re.sub(' 5:$', ' St', street)
            try:
                resp = geocode(housenum, street, borough)
                output.writerow({
                    'house_number': housenum,
                    'street': street,
                    'borough': borough,
                    'pound_code': pound_code,
                    'star_code': star_code,
                    'bbl': resp['address'].get('bbl'),
                    'zip_code': resp['address'].get('zipCode'),
                    'longitude': resp['address'].get('longitude'),
                    'latitude': resp['address'].get('latitude'),
                    'error': resp['address'].get('message')
                })
            except Exception as e:
                sys.stderr.write('error reading {path} row {rownum}: {error}\n'.format(
                    path=path,
                    rownum=rownum,
                    error=e
                ))


def process_csv(path, output):
    with open(path) as infile:
        reader = csv.DictReader(infile)
        for rownum, line in enumerate(reader):
            line.pop('')
            housenum = line['house_number']
            if '/' in housenum:
                housenum = housenum.split('/')[0]
            street = line['street']
            borough = line['borough']
            if line.get('bbl'):
                output.writerow(line)
            else:
                try:
                    resp = geocode(housenum, street, borough)
                    output.writerow({
                        'house_number': housenum,
                        'street': street,
                        'borough': borough,
                        'pound_code': line['pound_code'],
                        'star_code': line['star_code'],
                        'bbl': resp['address'].get('bbl'),
                        'zip_code': resp['address'].get('zipCode'),
                        'longitude': resp['address'].get('longitude'),
                        'latitude': resp['address'].get('latitude'),
                        'error': resp['address'].get('message')
                    })
                except Exception as e:
                    sys.stderr.write('error reading {path} row {rownum}: {error}\n'.format(
                        path=path,
                        rownum=rownum,
                        error=e
                    ))


if __name__ == '__main__':
    sys.argv.pop(0)
    has_header = sys.argv.pop(0)
    input_path = sys.argv.pop(0)

    output = csv.DictWriter(sys.stdout, HEADERS)
    if int(has_header):
        output.writeheader()

    if input_path.endswith('.csv'):
        process_csv(input_path, output)
    else:
        process_txt(input_path, output)
