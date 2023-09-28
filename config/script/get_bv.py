# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 11:52:31 2021

@author: tloree
"""

import io
import requests
import geopandas as gpd
from shapely import geometry, ops
import json
import xmltodict

def main(x,y,seuil):
    try:
        print("get BV")
        requete="https://geosas.fr/mntsurf/?service=WPS&version=1.0.0&request=Execute&identifier=xy2watershedcfl&datainputs=X=%s;Y=%s;ssbvSurf=%s" % (x,y,seuil)
        r = requests.get(url=requete)
        dico_bv=xmltodict.parse(r.text)

        a=dico_bv['wps:ExecuteResponse']['wps:ProcessOutputs']['wps:Output'][2]['wps:Data']
        for i in dico_bv['wps:ExecuteResponse']['wps:ProcessOutputs']['wps:Output']:

            if i['ows:Identifier'] == 'bvOut':
                a=i['wps:Data']
                b=(xmltodict.unparse(a, pretty=True))
        with io.BytesIO() as f:
            f.write(bytes(b,'utf-8'))
            f.seek(0)
            bv=gpd.read_file(f)
        if len(bv)==0:
            return "failed",'failed'
        print("BV saved, next explode bv")
        big_bv=bv.loc[bv.surface_ha ==bv.surface_ha.max() ]
        big_bv['bv']=0
        bv = bv.explode()
        multi_line = geometry.MultiLineString(bv.geometry.exterior.values)
        merged_lines = ops.linemerge(multi_line)
        border_lines = ops.unary_union(merged_lines)
        decomposition = ops.polygonize(border_lines)

        bv=gpd.GeoDataFrame()
        z=0
        for p in decomposition:
            bv.loc[z,'geometry']=p
            z+=1
        bv['surface_ha']=bv.geometry.area/10000
        bv=bv.set_crs("EPSG:2154")

        bv.geometry=bv.geometry.buffer(-0.001)
        bv=bv[bv.surface_ha>1]
        bv['bv'] = range(1,1+len(bv))
        bv.surface_ha=round(bv.surface_ha,1)
        bv=bv[["bv","geometry","surface_ha"]]
        big_bv=big_bv[["bv","geometry","surface_ha"]]

        dataFile_bv = json.loads(bv.to_json())
        dataFile_big_bv = json.loads(big_bv.to_json())

    except Exception as e:
        print(e)
        dataFile_bv='failed'
        dataFile_big_bv='failed'


    return dataFile_bv, dataFile_big_bv
