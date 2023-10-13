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
import enhancedV


LOGGER = logging.getLogger(__name__)

#utiliser ce logger

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.2.0',
    'id': 'enhanced-viz',
    'title': {
        'en': 'Visualise sensorthing aggregate',
        'fr': 'Visualisation d\'une chronique sensorthings aggrégée'
    },
    'description': {
        'en': 'Cette fonction génère automatiquement une chronique aggrégé à un pas de temps défini à partir d\'une url sensorthings',
        'fr': 'Cette fonction génère automatiquement une chronique aggrégé à un pas de temps défini à partir d\'une url sensorthings'
    },
    'keywords': ['timeseries', 'sensorthings', 'STA'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geosas.fr/sofair',
        'hreflang': 'fr-FR'
    }],
    'inputs': {
        'url_sensorthings': {
            'title': 'url datastream',
            'description': 'url du datastream',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'aggregation': {
            'title': 'aggregation',
            'description': 'methode d\'aggrégation (min,max,mean,median,sum)',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'echelle': {
            'title': 'echelle',
            'description': 'echelle de comparaison (year)',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        },
        'year_etude': {
            'title': 'year etude',
            'description': 'année cible',
            'schema': {
                'type': 'integer'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['message']
        }
    },
    'outputs': {
        'url_plot': {
            'title': 'url plot',
            'description': 'Url du plot',
            'schema': {
                'type': 'string'
            },
        }
    },
    'example': {
        'inputs': {
            'url_sensorthings': 'https://api.geosas.fr/agri4cast/v1.0/Datastreams(100)',
            'aggregation':'mean',
            'echelle':'year',
            'year_etude':2022
        }
    }
}

class enhancedVizProcessor(BaseProcessor):
    """enhancedViz Processor"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.enhancedViz.enhancedVizProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):
        print("ok enhancedViz go")

        mimetype = 'application/json'
        url_sensorthings = data.get('url_sensorthings', None)


        if url_sensorthings is None:
            outputs = {
                        'response': "Cannot process without a STA url"
            }
            return mimetype, outputs
            #raise ProcessorExecuteError('Cannot process without a url_st')
        aggregation = data.get('aggregation', None)
        echelle = data.get('echelle', None)
        year_etude = data.get('year_etude', None)
        #download data
        print("Start process")

        idprocess= datetime.datetime.now().strftime("%y%m%d_%H%M%S%f")

        url_plot = enhancedV.main(url_sensorthings, year_etude, idprocess, config)

        if url_plot !='failed':
            outputs = {
                    'url_plot': url_plot
            }

        else:

            outputs = {
                        'response': "failed"
                        }

        return mimetype, outputs

    def __repr__(self):
        return '<enhancedVizProcessor> {}'.format(self.name)
