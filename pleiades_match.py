#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    pleiades_match.py

    Match pleiades places with toponyms
"""

import requests
import os
import sys
import csv
import json
import gzip
import time
import argparse
from geopy.distance import geodesic
from jellyfish import jaro_distance


PLEIADES = 'datasets/pleiades-places-latest.json'
TOPONYMS = 'datasets/all_toponyms.json'


with open(PLEIADES) as pleiades_file:
    pleiades_json = json.load(pleiades_file)

pleiades_places = pleiades_json["@graph"]

with open(TOPONYMS) as toponyms_file:
    toponyms_places = json.load(toponyms_file)


# pleiades_

print("Decoded JSON Data From File")
p_places = []
for item in pleiades_places:
    if item['names']:
        p_place_item = {}
        names = item['names']
        p_place_names = []
        for name in names:
            p_place = {}
            p_place['name'] = name['romanized']
            p_place['language'] = name['language']
            p_place_names.append(p_place)
        p_place_item['names'] = p_place_names
        coordinates = {}
        if item['reprPoint']:
            coordinates['latitude'] = item['reprPoint'][1]
            coordinates['longitude'] = item['reprPoint'][0]
        p_place_item['coordinates'] = coordinates
        item['reprPoint']
        p_place_item['iri'] = item['uri']

        p_places.append(p_place_item)
        # print(item['reprPoint'])
        # print(item['uri'])
    # sys.exit()
print("Done reading json file")

# print(p_places)
toponyms = []
for t_place in toponyms_places:
    coords_t = (t_place['latitude'], t_place['longitude'])

    for p_place in p_places:
        # print(p_place)
        if p_place['coordinates']:
            coords_p = (p_place['coordinates']['latitude'], p_place['coordinates']['longitude'])
            if geodesic(coords_t, coords_p).km <= 10:
                for place in p_place['names']:
                    if jaro_distance(place['name'], t_place['name']) >= 0.85 :
                        print("IMAGO toponym: " + t_place['name'])
                        print("pleiades toponym: " + place['name'])
                        print(geodesic(coords_t, coords_p).km)
                        t_place['iri_pleiades'] = p_place['iri']
                        break;

    toponyms.append(t_place)

with open("toponimi.json", 'w', encoding='utf-8') as f:
    json.dump(toponyms, f, ensure_ascii=False)

# coords_1 = (52.2296756, 21.0122287)
# coords_2 = (52.406374, 16.9251681)
#
# print geopy.distance.vincenty(coords_1, coords_2).km
