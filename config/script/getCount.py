#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:30:30 2023
@author: hsquividant
"""

import sys
import os 
import requests
import logging
from optparse import OptionParser
from database import loadInstancesFile, writeInstancesFile

parser = OptionParser()
parser.add_option("-f", "--instancesFile", dest="instancesFile",
                  default="",
                  help="Fichier contenant la liste des instances SensorThings", type="str")
parser.add_option("-u", "--stauURL", dest="staURL",
                  default="",
                  help="STA URL service to query", type="str")
parser.add_option("-a", "--all",
                  action="store_true", dest="allInstances", default=False,
                  help="Query all STA instances included in instanceFile")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose mode")

(options, args) = parser.parse_args()

staURL = options.staURL
allInstances= options.allInstances


if options.verbose == True :
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def getCount (url) :
    """
Returns dict {'nb_things, 'nb_observedProperties','nb_observations'} by querying input URL.

Arguments:
url  – STA service URL to query. e.g. https://sensorthings.geosas.fr/rennesmetro/v1.0/
  
"""
    instance = {"nb_things": 0, "nb_observedProperties": 0, "nb_observations": 0}
    # Get number of Things in "url" STA 
    try:
        r=requests.get(url+"/Things?$count=true")
        r.raise_for_status()
        instance["nb_things"]=int(r.json()['@iot.count'])
    except requests.exceptions.HTTPError as e:
        logging.error (e.response.text)

    # Get number of ObservedProperties in "url" STA 
    try:
        r=requests.get(url+"/ObservedProperties?$count=true")
        r.raise_for_status()
        instance["nb_observedProperties"]=int(r.json()['@iot.count'])
    except requests.exceptions.HTTPError as e:
        logging.error (e.response.text)

    # Get number of Observations in "url" STA 
    try:
        r=requests.get(url+"/Observations?$count=true")
        r.raise_for_status()
        instance["nb_observations"]=int(r.json()['@iot.count'])
    except requests.exceptions.HTTPError as e:
        logging.error (e.response.text)    
        
    return instance       

def actualizeCountForAllInstances () :
    """
Actualize the dict {'nb_things, 'nb_observedProperties','nb_observations'} for all instances in instanceFile.
  
"""
    for i in baseJsonST:
        i2=getCount(i["url"])
        writeInstancesFile(i["url"],i2)

def actualizeCountForOneInstance (url) :
    """
Actualize the dict {'nb_things, 'nb_observedProperties','nb_observations'} for all instances in instanceFile.
  
"""
    if url != None :
        i=getCount(url)
        writeInstancesFile(url,i)

# main
try:
    baseJsonST = loadInstancesFile()
    if allInstances == True:
       actualizeCountForAllInstances ()
    else :
        actualizeCountForOneInstance (staURL)
finally:
    logging.info ("---------------- End of getCount -----------------")

