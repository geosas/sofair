import logging
import requests
import json
import requests
import json
import geopandas as gpd
from sqlalchemy import create_engine
import io
from jinja2 import Environment, FileSystemLoader
import uuid
import datetime
import os
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
import sys

from .setupProcess import confProcess
sys.path.insert(1, confProcess().pathWd)
from setup import confLoading
config = confLoading()


LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'sta_to_sdi',
    'title': {
        'en': 'Publishes a SensorThings service in an IDG',
        'fr': 'Publie un service SensorThings dans une IDG'
    },
    'description': {
        'en': 'This process publishes INPIRE-compliant layer and metadata from a SensorThings service to a Spatial Data Infrastructure.',
        'fr': 'Cette fonction publie dans une Infrastructure de Données Géographiques (IDG) une couche et une métadonnée à partir d\'un service SensorThings.',
    },
    'keywords': ['SensorThings', 'SDI', 'INSPIRE'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'url_st': {
            'title': 'url_st',
            'description': 'url du service sensorthing',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'abstract': {
            'title': 'abstract',
            'description': 'abstract pour les métadonnées',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'author': {
            'title': 'author',
            'description': 'auteur de la couche',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'geoserver_title': {
            'title': 'geoserver_title',
            'description': 'Titre de la futur couche dans geoserver',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        }
    },
    'outputs': {
        'response': {
            'title': 'Log de creation',
            'description': 'Informe de la creation ou non de la couche',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'url_st': 'https://api.geosas.fr/onde/v1.0/',
        }
    }
}

def downloadST(url_serveur):
    r=requests.get(url=url_serveur)
    print(r.status_code)
    things_agri=r.json()['value']
    while '@iot.nextLink' in r.json() :
        print("get nextlink")
        r=requests.get(r.json()['@iot.nextLink'])
        things_agri= things_agri+ r.json()['value']
    return things_agri

def create_geojson(data, urlSt):
    my_dict={ "type": "FeatureCollection","features":[]}

    for i in data:
        try:
            i['Locations'][0]['location']['geometry']
            #print("bon format")
            loc=i['Locations'][0]['location']
        except:
            print("pas le bon format, repare geom")
            loc={}
            loc['type']='Feature'
            loc['geometry']={
                'type': i['Locations'][0]['location']['type'],
                'coordinates': i['Locations'][0]['location']['coordinates']
                }
        url_thing= "%sThings(%s)" % (urlSt,i['@iot.id'] )
        loc['properties']={'id':i['@iot.id'],'name':i['name'],'description':i['description'],'thingsUrl':url_thing}

        my_dict["features"].append(loc)

    json_string = json.dumps(my_dict)
    f = io.StringIO(json_string)
    return f

def publie_couche(pg_table,service_url, workspace, name_entrepot,auth_x):

    print("active couche %s" % pg_table)
    headers_x = {'Content-Type': 'text/xml'}
    data_x="<featureType><name>{}</name></featureType>".format(pg_table)
    url_x="{}/rest/workspaces/{}/datastores/{}/featuretypes".format(
                        service_url, workspace, name_entrepot)

    r = requests.post(url=url_x, headers=headers_x, auth=auth_x, data=data_x)
    print(str(r.status_code))
    print(r.text)
    print("creation couche %s finish" % pg_table)
    return r.status_code,r.text

def publie_couche_metadonnee(abstract, author, pg_table, titre_geoserver, url_sta):
    print('publication geoserver et geonetwork')
    print('creation json')
    try:
        dico_jinja={
        "layerName": pg_table,
        "layerNameIds" : pg_table,
        "layerNameDb": pg_table,
        "theGeomName": "geometry",
        "workspace": "sensorthings",
        "storeIds": "sensorthings store",
        "layerTitle": titre_geoserver,
        "uuid": str(uuid.uuid4()),
        "metadataTitle": titre_geoserver,
        "creationDate": datetime.datetime.now().strftime('%Y-%m-%d'),
        "abstract": abstract,
        "url_sta": url_sta,
        "author": author
        }

        environment = Environment(loader=FileSystemLoader(config.pathData[:-1]))
        template = environment.get_template("sensorthings-metadata-iso19139.json")

        filename = "/data/ids/2ids/2ids_metadata/json/"+pg_table+".json"
        content = template.render(**dico_jinja)
        with open(filename, mode="w", encoding="utf-8") as message:
            message.write(content)
        print('publish by 2ids')
        a=os.system("/data/ids/2ids/2ids/2ids publish %s" %(pg_table))

        print(a)
        if a==0:
            return 201
        else:
            return "erreur publication métadonnées"
    except Exception as e:
        print(e)
        return e





class STAToSDIProcessor(BaseProcessor):
    """Test STAToSDI Processor"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.STAToSDI.STAToSDIProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)



    def execute(self, data):
        print("ok st go")

        mimetype = 'application/json'

        url_st = data.get('url_st', None)
        if url_st is None:
            outputs = {
                        'response': "Cannot process without a url_st"
            }
            return mimetype, outputs
            #raise ProcessorExecuteError('Cannot process without a url_st')
        abstract =  data.get('abstract', None)
        author = data.get('author', None)
        titre_geoserver = data.get('geoserver_title', None)

        #download data
        print("download data from ST")
        try:
            data=downloadST(url_st+"Things?$top=2000&$select=name,description,id&$expand=Locations($select=location),Datastreams($select=name,Observations)")
        except:
            outputs = {
                        'response': "Impossible de télécharger les Things, erreur dans l'url ou côté serveur ST : %s" % (url_st)
            }
            return mimetype, outputs

        #creation couche vecteur
        print("create vector")
        try:
            couche=create_geojson(data, url_st)
            station=gpd.read_file(couche)
            station=station.set_crs('EPSG:4326')
        except:
            outputs = {'response':"Impossible de créer les géometries sources, verifier le format des géométrie du serveur ST conforme à l'url du standard",
            "url standard":"https://docs.ogc.org/is/18-088/18-088.html#location"
            }
            return mimetype, outputs

        #publish PSQL
        print("create engine")
        db = create_engine(config.conn_string)
        pg_table=url_st.split('/')[-3]
        print("publish PSQL")
        try:
            station.to_postgis(pg_table, con=db, if_exists='replace',schema='sensorthings')
        except :
            outputs ={'response':"impossible de créer la couche dans la BDD"}
            return mimetype, outputs

        db.dispose()
        print("dispose and close engine")
        #publish geoserver
        print("publish geoserver")
        #retour,retour_txt=publie_couche(pg_table,config.service_url, config.workspace, config.name_entrepot, config.auth_x)
        retour = publie_couche_metadonnee(abstract, author, pg_table, titre_geoserver, url_st)

        if retour==201:
            outputs = {
                    'response': "c'est ok la couche est publiée",
                    'url_info':'%s/%s/wms?service=wms&request=DescribeLayer&layers=%s&version=1.1.1&outputFormat=application/json' % (config.service_url,config.workspace,pg_table)
                    }
        else:
            outputs = {
                        'response': "erreur de publicationr",
                        'retour du serveur':retour
                        }

        return mimetype, outputs

    def __repr__(self):
        return '<STAToSDIProcessor> {}'.format(self.name)
