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
sys.path.insert(1, config.pathScript)
import autoST



LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'create-config-xlsx',
    'title': {
        'en': 'Setting up the sensorthings service',
        'fr': 'Configuration du service SensorThings'
    },
    'description': {
        'en': 'This function uploads an XLSX file to create the various objects in the SensorThings service: Things, Sensors, Observed Properties, Locations, Features Of Interest and Datastreams.',
        'fr': 'Cette fonction permet d\'uploader un fichier XLSX afin de créer les différents objets du service SensorThings : Things, Sensors, Observed Properties, Locations, Features Of Interest et Datastreams.',
    },
    'keywords': ['SensorThings','setup'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'name_config_xlsx': {
            'title': 'name_config_xlsx',
            'description': 'Nom du fichier de config xlsx complété',
            'schema': {
                'type': 'text/plain'
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
            'description': 'Informe de la creation ou non de la cnfig',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'config_xlsx': 'aghrys_sensorthings.xlsx',
        }
    }
}





class createConfigXLSXProcessor(BaseProcessor):
    """Test creationConfigXLSX Processor"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.createConfigXLSX.createConfigXLSXProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)



    def execute(self, data):
        print("ok st go")

        mimetype = 'application/json'

        config_xlsx = data.get('config_xlsx', None)
        if config_xlsx is None:
            outputs = {
                        'response': "Cannot process without a xlsx path"
            }
            return mimetype, outputs
            #raise ProcessorExecuteError('Cannot process without a url_st')


        path_config=os.path.join(config.dir_xlsx, config_xlsx)
        print("start création config",path_config)

        #try:
        retour=autoST.main(path_config, config.username, config.password)
        outputs = {
            'response': retour
        }
        #except:
        #    outputs = {
        #                'response': "erreur inconnu"
        #    }

        return mimetype, outputs

    def __repr__(self):
        return '<createConfigXLSXProcessor> {}'.format(self.name)
