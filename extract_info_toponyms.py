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
    wdQuery = f'\nSELECT DISTINCT ?label ?coordinate\
                WHERE {{\
                    wd:{qid} rdfs:label ?label; \
                    OPTIONAL{{\
                      wd:{qid} wdt:P625 ?coordinate .\
                    }}\
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
def wikiInteractive(wdEntities, qid, extra=''):
    
    # print(wdEntities)
    place = {}
    for entity in wdEntities:
        printed = True
        # print(entity)
        if "label" in entity:
            if entity["label"]['xml:lang']=='en':
                name_en = entity["label"]["value"]
                place['label_en'] = name_en
            if entity["label"]['xml:lang']=='it':
                name_it = entity["label"]["value"]
                place['label_it'] = name_it
            
        if "coordinate" in entity:
            coord = entity["coordinate"]["value"]
            res = re.findall(r'\(.*?\)', coord)
            coord = res[0].split()
            place['latitude'] = coord[1][:-1]
            place['longitude'] = coord[0][1:]
        else:
            place['latitude'] = ""
            place['longitude'] = ""
        

        place['iri'] = 'http://www.wikidata.org/entity/'+qid
    
    print(place)    
    # print(place['label_en'] + " "  +place['label_it'] + " " + place['latitude'] + " " + place['longitude'])
    
    # print(places)
    return place
    # f'http://www.wikidata.org/entity/{qid}', qid
        
def findPlace(toponym, object):
    with open("places_full_new.json") as p_file:
        all_ps = json.load(p_file)
        for p in all_ps:
            if toponym == p: 
                obj = all_ps[p]
                if object == "labelIta":
                    return obj["label_it"]
                if object == "labelEng":
                    return obj["label_en"]
                if object == "iri":
                    return obj["iri"]
                if object == "latitude":
                    return obj["latitude"]
                if object == "longitude":
                    return obj["longitude"]

def findIriWork(work):
    if work == "Monarchia":
        return "https://www.wikidata.org/entity/Q134221"
    if work == "Egloge":
        return "https://www.wikidata.org/entity/Q921273"
    if work == "Epistole":
        return "https://www.wikidata.org/entity/Q3730666"
    if work == "De Vulgari Eloquentia":
        return "https://www.wikidata.org/entity/Q18081"
    if work == "Questio de Aqua et Terra":
        return "https://imagoarchive.it/entity/Questio"

# Pleiades names
pleiades = {}
with open("pleiades-names.csv", encoding='utf-8') as p:
    csv_pleiades = csv.reader(p, delimiter=',')
    for i, row in enumerate(csv_pleiades):
        pleiades[row[14]] = row[14]
        # print(row[14])


# inizio la ricerca
# all_places = {}
# with open("toponimi.json") as toponyms_file:
#     all_toponyms = json.load(toponyms_file)

# # print(all_toponyms)

# for toponym in all_toponyms:
#     print()
#     print(toponym)
#     name = toponym
#     # print(all_toponyms[toponym])
#     for key, value in all_toponyms[toponym].items():
#         iri = key
#         # print(value['qid'])

#         qid = iri.split('/')[-1]
#         wdEntities = wdQuery(qid)
#         places = wikiInteractive(wdEntities, qid)
#         # print(places)
        
#         all_places[toponym] = places
#         with open(PLACES_FILE, 'w', encoding='utf-8') as f:
#             json.dump(all_places, f, ensure_ascii=False)

all_places = {}
print('   === Places search ===\n')
with open(CSV_FILE, encoding='utf-8') as f:
    csv_toponimi = csv.reader(f, delimiter=',')


# For each row of the CSV...
# count_all = 0
# count_empty = 0
# count_founded = 0
# count_founded_pleiades = 0
# old_place = ""

    toponnyms = []
    for i, row in enumerate(csv_toponimi):
        toponym = {}
        toponym['name'] = row[20]
        toponym['lemma'] = row[14]
        toponym['form'] = row[13]
        toponym['labelIta'] = findPlace(row[20], "labelIta") # search in json place_full_new
        toponym['labelEng'] = findPlace(row[20], "labelEng") # search in json place_full_new
        work = {}
        work['name'] = row[18]
        work['iri'] = findIriWork(row[18])
        toponym['work'] = work
        toponym['occDeVulgari'] = row[4]
        toponym['occEgloge'] = row[5]
        toponym['occEpistole'] = row[6]
        toponym['occMonarchia'] = row[9]
        toponym['occQuestio'] = row[10]
        toponym['totOccurrences'] = row[17]
        toponym['context'] = row[12]
        toponym['urlDS'] = row[15]
        toponym['placeText'] = row[16]
        toponym['position'] = row[19]
        toponym['iriWD'] = findPlace(row[20], "iri") # search in json place_full_new
        toponym['latitude'] = findPlace(row[20], "latitude") # search in json place_full_new
        toponym['longitude'] = findPlace(row[20], "longitude") # search in json place_full_new
        toponym['VDLlemma'] = ""
    
        toponnyms.append(toponym)
        
    with open("all_toponyms.json", 'w', encoding='utf-8') as f:
        json.dump(toponnyms, f, ensure_ascii=False)
        
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
