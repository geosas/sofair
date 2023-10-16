#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:30:30 2023
@author: hsquividant
"""

import sys
import os 
import json
import logging

# adding the parent directory to the sys.path.
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# load config
from setup import confLoading
config = confLoading()

instancesFile = confLoading().pathStatic+"json/STAInstances.json"

def loadInstances () :
    with open(instancesFile, encoding='utf-8') as json_src: 
        baseJsonST = json.load(json_src)
    return baseJsonST['instances']

 
def updateInstance (url,instance) :
    """
write the instanceFile by changing the key/value in "instance" for the "url" input.

Arguments:
url      - STA service URL . e.g. https://sensorthings.geosas.fr/rennesmetro/v1.0/
instance - dict containing the key/val to change and save in the instancesFile 
  
"""
    logging.info ("--- %s ---", url)
    with open(instancesFile, encoding='utf-8') as json_src: 
        baseJsonST = json.load(json_src)
    baseJsonST = baseJsonST['instances']    
    for i in baseJsonST:
        if i["url"] == url:
            logging.info ("--- %s ---", url)
            for key, val in instance.items():
                i[key] = val
                logging.info (key + "%s: Old value=%s / New value=%s", key, str(i[key]), str (instance[key]))
            staInstances = {"instances":baseJsonST} 
            json_object = json.dumps(staInstances, indent=4)
            with open(instancesFile, "w") as outfile:
                outfile.write(json_object)           

def createInstance (instance) :
    """
create a new STA instance in the instanceFile.

Arguments:
instance - dict containing the key/val of the new STA instance and save in the instancesFile 
  
"""
    with open(instancesFile, encoding='utf-8') as json_src: 
        baseJsonST = json.load(json_src)
    baseJsonST = baseJsonST['instances']    
    baseJsonST.append(instance)
    staInstances = {"instances":baseJsonST} 
    json_object = json.dumps(staInstances, indent=4)
    with open(instancesFile, "w") as outfile:
        outfile.write(json_object)           