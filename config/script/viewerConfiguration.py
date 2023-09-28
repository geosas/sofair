# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 11:52:31 2021

@author: tloree
"""
from jinja2 import Environment, FileSystemLoader
import requests
import xmltodict
from pyproj import Transformer
import numpy as np

def main(url_sensorthings, config):

    try:
        name=url_sensorthings.split('/')[-3]

        r = requests.get(url="%s/sensorthings/wms?service=wms&request=GetCapabilities&layer=%s&version=1.1.1" % (config.service_url, name))
        print(r.status_code)
        capabilities = xmltodict.parse(r.content.decode('utf-8'))

        for i in capabilities['WMT_MS_Capabilities']['Capability']['Layer']['Layer']:
            if i['Name'] != name:
                continue
            print(i['Name'])
            print(i['BoundingBox'])
            break

        transformer = Transformer.from_crs(i['BoundingBox']['@SRS'],"EPSG:3857")
        mini=transformer.transform(i['BoundingBox']['@miny'],i['BoundingBox']['@minx'])
        maxi=transformer.transform(i['BoundingBox']['@maxy'],i['BoundingBox']['@maxx'])

        bbox="%s, %s, %s, %s" % (mini[0], mini[1], maxi[0], maxi[1])
        print(bbox)
        center="%s, %s" % ( (mini[0]+maxi[0])/2, (mini[1]+maxi[1])/2)

        transformer = Transformer.from_crs( i['BoundingBox']['@SRS'], "EPSG:2154")
        mini=transformer.transform(i['BoundingBox']['@miny'],i['BoundingBox']['@minx'])
        maxi=transformer.transform(i['BoundingBox']['@maxy'],i['BoundingBox']['@maxx'])
        diff_x= abs( mini[0] - maxi[0])/1000

        if diff_x==0:
            diff_x=10
        #formule qui marche... pour bzh à voir ailleurs
        zoom=np.log((40075016.686 * abs(np.cos(float(i['BoundingBox']['@miny']))))/diff_x)/np.log(2)-8

        dico_jinja={
            'name':name,
            'url':url_sensorthings,
            'center':center,
            'zoom':zoom}

        environment = Environment(loader=FileSystemLoader(config.pathStatic+"configMviewer"))
        template = environment.get_template("exemple.xml")

        filename = config.pathStatic+"configMviewer/"+name+".xml"
        content = template.render(**dico_jinja)

        with open(filename, mode="w", encoding="utf-8") as message:
            message.write(content)


        url_config=config.url_sofair_static+'configMviewer/'+name+'.xml'
        url_mviewer=config.url_Mviewer_geosas+url_config
        print("creation finish")

    except Exception as e:
        print(e)
        url_mviewer='failed'

    return url_mviewer, url_config