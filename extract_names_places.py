#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    wd_search.py

    Wikidata API
    `Search` module: Search for a library

    MIT License
"""

import requests
import os
import sys
import csv
import json
import gzip
import time
import argparse
import urllib.parse
import urllib.request
import re
import certifi

# Inizializza la sessione
S = requests.Session()

# Wikidata query URL sparql
WD_URL = 'https://query.wikidata.org/sparql?query='
# URL per la query alle api della ricerca su Wikidata
URL = "https://www.wikidata.org/w/api.php"
# path del file input, in questo caso la lista
# delle biblioteche
CSV_FILE = 'toponimi.csv'
LIBRARY_FILE = 'libraries.json'
PLACES_FILE = 'places_full_new.json'
PLACE_PATH = 'place_complete.json'

# Function to load a URL and return the content of the page
def loadURL(url, encoding='utf-8', asLines=False):
    
    request = urllib.request.Request(url)

    # Set headers
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows)')
    request.add_header('Accept-Encoding', 'gzip')

    # Try to open the URL
    try:
        myopener = urllib.request.build_opener()
        f = myopener.open(request, timeout=120)
        url = f.geturl()
    except (urllib.error.URLError, urllib.error.HTTPError, ConnectionResetError):
        raise
    else:
        # Handle gzipped pages
        if f.info().get('Content-Encoding') == 'gzip':
            f = gzip.GzipFile(fileobj=f)
        # Return the content of the page
        return f.readlines() if asLines else f.read().decode(encoding)
    return None

# Function to perform a Wikidata query
def wdQuery(qid):

    # Define SPARQL query
    wdQuery = f'\nSELECT DISTINCT ?label\
                WHERE {{\
                    wd:{qid} rdfs:label ?label; \
                    FILTER(lang(?label)="en" || (LANG(?label)) = "it") \
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],it,la,en,fr,es,de". }}\
                }}'

    # Load query URL
    results = loadURL(f'{WD_URL}{urllib.parse.quote(wdQuery)}&format=json')

    # Return results
    if results:
        return json.loads(results)['results']['bindings']
    else:
        print(f'   Not found')
    return None

# Interactive Wikidata search
def wikiInteractive(wdEntities):
    
    # print(wdEntities)
    # place = {}
    name_it = ""
    for entity in wdEntities:
        printed = True
        # print(entity)
        if "label" in entity:
            if entity["label"]['xml:lang']=='en':
                name_en = entity["label"]["value"]
                # place['label_en'] = name_en
            if entity["label"]['xml:lang']=='it':
                name_it = entity["label"]["value"]
                # place['label_it'] = name_it
        
    
    # print(place)    
    # print(place['label_en'] + " "  +place['label_it'] + " " + place['latitude'] + " " + place['longitude'])
    
    # print(places)
    return name_it, name_en
    # f'http://www.wikidata.org/entity/{qid}', qid
        



# inizio la ricerca
all_places = {}
with open(PLACE_PATH, encoding='utf-8') as place_file:
    places = json.load(place_file)

    # For each author in file (sorted alphabetically)
    for place in sorted(places.values(), key=lambda x: x['name']):

        # Get author fields
        iri = place['iri'].strip()
        name = place['name'].strip()
        country = place['country'].strip()
        coord = place['coord'].strip()
        qid = iri.split('/')[-1]
        wdEntities = wdQuery(qid)
        name_it, name_en = wikiInteractive(wdEntities)
        alias = []
        if name_it != "":
            alias.append(name_en)
            alias.append(name)
            place['name'] = name_it
        else:
            alias.append(name_en)
            alias.append(name)
            place['name'] = name_en
        
        place['alias'] = alias
        print(place)
        
        all_places[name] = place


        
with open("place_complete_2.json", 'w', encoding='utf-8') as f:
    json.dump(all_places, f, ensure_ascii=False)
        
#         if old_place != row[20]:
#             old_place = row[20]
#             count_all = count_all + 1
#             # print(old_place)
            
#             pl_res = [val for key, val in pleiades.items() if old_place in key]
#             if pl_res:
#                 count_founded_pleiades = count_founded_pleiades + 1
#                 # if old_place in pleiades.values():
#                 print(old_place)
                    
#             wdEntities = wdQuery(old_place)
#             places = wikiInteractive(wdEntities)
#             if not places:
#                 count_empty = count_empty + 1
#                 # print(old_place)
#                 # res = [val for key, val in pleiades.items() if old_place in key]
#                 # if res:
#                 # # if old_place in pleiades.values():
#                 #     print(old_place)
#             else:
#                 count_founded = count_founded + 1
                

#             all_places[row[20]] = places
#             with open(PLACES_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(all_places, f, ensure_ascii=False)
            
#             # res2 = [val for key, val in pleiades.items() if old_place in key]
#             # if res2:
#             # # if old_place in pleiades.values():
#             #     count_founded_pleiades = count_founded_pleiades + 1
        
#     print("Tutti i toponimi " +  str(count_all))
#     print("Luoghi trovati wikidata " +  str(count_founded))
#     print("Luoghi non trovati wikidata " +  str(count_empty))
#     print("Luoghi trovati pleiades " +  str(count_founded_pleiades))


# data = json.load(open(LIBRARY_FILE))
# #print(len(data))
# places = {}
# for key in data.keys():
#     value = data.get(key, None)
#     gpe = value['gpe']

#     if gpe:
    
#         place = {}

#         # Get the Wikidata ID
#         qid = gpe.split('/')[-1]

#         wdEntities = wdQuery(qid)
#         if wdEntities:
#             wdIRI, name = wikiInteractive(wdEntities, qid)
#             place['iri'] = wdIRI
#             place['name'] = name
#             # print(name)
        
      
#         if name not in places:
#             places[place['name']] = place
#         # print(places)
#         with open(PLACES_FILE, 'w', encoding='utf-8') as f:
#             json.dump(places, f, ensure_ascii=False)
