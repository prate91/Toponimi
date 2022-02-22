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

# Inizializza la sessione
S = requests.Session()

# Wikidata query URL sparql
WD_URL = 'https://query.wikidata.org/sparql?query='
# URL per la query alle api della ricerca su Wikidata
URL = "https://www.wikidata.org/w/api.php"
# path del file input, in questo caso la lista dei toponimi
CSV_FILE = 'toponimi.csv' # CSV con le entità
LIBRARY_FILE = 'libraries.json'
PLACES_FILE = 'places.json'

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
def wdQuery(entity_label):

    # Define SPARQL query
    wdQuery = f'\nSELECT DISTINCT ?entity ?label\
                WHERE {{\
                    ?entity rdfs:label "{entity_label}"@en ; \
                            rdfs:label ?label . \
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
    
    print(wdEntities)
    for entity in wdEntities:
        # print(entity)
        if "entity" in entity:
            iri = entity["entity"]["value"]
            name = entity["label"]["value"]
            print(iri + " " + name)
    
    # print(places)
    return iri, name
        


# inizio la ricerca
all_places = {}
print('   === Entity search ===\n')
with open(CSV_FILE, encoding='utf-8') as f:
    csv_entity = csv.reader(f, delimiter=',')


    # For each row of the CSV...
    
    for i, row in enumerate(csv_entity):
        # row[i] rappresenta il valore nella colonna i
        print(row[14])
        
        entity_to_search = row[14]
        
        wdEntities = wdQuery(entity_to_search)
        iri, names = wikiInteractive(wdEntities)
        
        