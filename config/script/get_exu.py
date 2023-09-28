# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 11:52:31 2021

@author: tloree
"""
import os
import requests
import geopandas as gpd
import sys
import argparse
import io
import json


def main(surface_min):
    """Post a request to MNTSurf, save the outlet of Britany.
    :param surface_min: surface minimale des bassins versants\
    des exutoires
    :param wd: Working directory
    :type wd: string
    :param logger: Logger object
    :type logger: object
    :return: Output file path or failed message
    :rtype: string
    """
    requete="https://geosas.fr/mntsurf/?service=WPS&version=1.0.0&request=Execute&identifier=getOutlet&datainputs=mntin=Bretagne 50m;epsgOut=epsg:2154;seuilSbv=%s"% (surface_min)
    print("start request")
    try:
        r = requests.get(url=requete)
        if r.status_code==200:
            print("request ok")
            with io.BytesIO() as f:
                f.write(r.content)
                f.seek(0)
                gdf=gpd.read_file(f)
                print("output saved")
            gdf=gdf.drop(columns =['num','surface_ha'])
            gdf=gdf.set_crs('EPSG:2154')
            outfile=json.loads(gdf.to_json())
            print("getoutlet : done")

        return outfile
    except Exception as e:
        print(e)
        return 'failed'


if __name__ == "__main__":
    if len(sys.argv) == 1:
        prog = os.path.basename(sys.argv[0])
        print(sys.argv[0]+' [options]')
        print("Help : ", prog, " --help")
        print("or : ", prog, " -h")
        sys.exit(-1)
    else:
        usage = "usage: prog [options]"
        parser = argparse.ArgumentParser(description="getoulet process of\
                                                      MNTSurf")
        parser.add_argument("-surface_min", dest="surface_min", action="store",
                            help="surface minimale des bassins versants des exutoires",
                            required=True)
        parser.add_argument("-wd", dest="wd", action="store",
                            help="Working directory", required=True)
        args = parser.parse_args()


    output = main(args.surface_min)
    print(output)
    sys.exit()
