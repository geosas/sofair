import logging
import requests
import json
import requests
import json
import os
from pygeoapi.process.base import BaseProcessor
import sys

from .setupProcess import confProcess
sys.path.insert(1, confProcess().pathWd)
from setup import confLoading
config = confLoading()
sys.path.insert(1, config.pathScript)
import autoSTData


LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'post-observations',
    'title': {
        'en': 'Upload observations',
        'fr': 'Ajout d\'observations'
    },
    'description': {
        'en': 'This function uploads observations from CSV or XLSX file to the SensorThings service.',
        'fr': 'Cette fonction transfère les observations présentes dans un fichier CSV ou XLSX dans le service SensorThings.',
    },
    'keywords': ['Upload', 'SensorThings'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'data_file': {
            'title': 'data_file',
            'description': 'Nom du fichier de data xlsx ou csv',
            'schema': {
                'type': 'text/plain'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'mode': {
            'title': 'mode',
            'description': 'mode long ou large',
            'schema': {
                'type': 'text/plain'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'colonne_date': {
            'title': 'colonne_date',
            'description': 'nom de la colonne date',
            'schema': {
                'type': 'text/plain'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'format_date': {
            'title': 'format_date',
            'description': 'format de la date exemple %Y%m%d',
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
            'title': 'Log de post',
            'description': 'Informe du post ou non des data',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'data_file': 'meteo_sensorthings.csv',
            'mode':'large',
            'format_date':'%Y%m%d',
            'colonne_date':'date'
        }
    }
}





class postObservationsProcessor(BaseProcessor):
    """Test postObservations Processor"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.postObservations.postObservationsProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)



    def execute(self, data):
        print("ok st go")

        mimetype = 'application/json'

        data_xlsx = data.get('data_file', None)
        if data_xlsx is None:
            outputs = {
                        'response': "Cannot process without a xlsx or csv path"
            }
            return mimetype, outputs
            #raise ProcessorExecuteError('Cannot process without a url_st')
        mode=data.get('mode', None)
        print(mode)
        colonne_date = data.get('colonne_date', None)
        format_date = data.get('format_date', None)


        path_config=os.path.join(config.dir_xlsx_data, data_xlsx)
        print("start création config",path_config)

        #try:

        retour=autoSTData.main(path_config, colonne_date, format_date, config.username, config.password)
        outputs = {
            'response': retour
        }
        #except:
        #    outputs = {
        #                'response': "erreur inconnu"
        #    }

        return mimetype, outputs

    def __repr__(self):
        return '<postObservationsProcessor> {}'.format(self.name)
