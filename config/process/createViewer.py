import logging
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
import datetime
import sys
from pathlib import Path

from .setupProcess import confProcess
sys.path.insert(1, confProcess().pathWd)
from setup import confLoading
config = confLoading()
sys.path.insert(1, config.pathScript)
import viewerConfiguration


LOGGER = logging.getLogger(__name__)

#utiliser ce logger

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'create-viewer',
    'title': {
        'en': 'Create SensorThings geographic portal',
        'fr': 'Création d un visualiseur SensorThings'
    },
    'description': {
        'en': 'This function automatically generates a URL pointing to a map portal displaying chronicles of observations from the SensorThings service provided.',
        'fr': 'Cette fonction génère automatiquement une URL qui pointe vers un portail cartographique proposant la visualisation des chroniques des observations du service SensorThings fourni.'
    },
    'keywords': ['mviewer', 'sensorthings', 'STA'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geosas.fr/sofair',
        'hreflang': 'fr-FR'
    }],
    'inputs': {
        'url_sensorthings': {
            'title': 'url STA',
            'description': 'url du service Sensorthings',
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
        'url_mviewer': {
            'title': 'url viewer',
            'description': 'Url du mviewer',
            'schema': {
                'type': 'string'
            },
        },
        'url_config': {
            'title': 'url config',
            'description': 'Url du fichier de configuration du mviewer',
            'schema': {
                'type': 'string'
            },
        }
    },
    'example': {
        'inputs': {
            'url_sensorthings': 'https://api.geosas.fr/wsci/v1.0/'
        }
    }
}

class createViewerProcessor(BaseProcessor):
    """createViewer Processor"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.createViewer.createViewerProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):
        print("ok createViewer go")

        mimetype = 'application/json'
        url_sensorthings = data.get('url_sensorthings', None)


        if url_sensorthings is None:
            outputs = {
                        'response': "Cannot process without a STA url"
            }
            return mimetype, outputs
            #raise ProcessorExecuteError('Cannot process without a url_st')

        #download data
        print("Start process")

        idprocess= datetime.datetime.now().strftime("%y%m%d_%H%M%S%f")

        url_mviewer, url_config = viewerConfiguration.main(url_sensorthings, config)

        if url_mviewer !='failed':
            outputs = {
                    'url_mviewer': url_mviewer,
                    'url_config': url_config
                    }

        else:

            outputs = {
                        'response': "failed"
                        }

        return mimetype, outputs

    def __repr__(self):
        return '<createViewerProcessor> {}'.format(self.name)
