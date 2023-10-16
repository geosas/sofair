# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2022 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
import sys
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from .setupProcess import confProcess
sys.path.insert(1, confProcess().pathWd)
from setup import confLoading
config = confLoading()
sys.path.insert(1, config.pathScript)
import createSTA


LOGGER = logging.getLogger(__name__)

#: Process metadata and description
PROCESS_METADATA = {
    'version': '0.1',
    'id': 'create-sta',
    'title': {
        'en': 'SensorThings API creation',
        'fr': 'Création d\'instance SensorThings'
    },
    'description': {
        'en': 'This function allows you to create a new instance of a SensorThings service that is immediately accessible online.',
        'fr': 'Cette fonction permet la création d\'une nouvelle instance d\'un service SensorThings immédiatement accessible en ligne.',
    },
    'keywords': ['OGC', 'sensorthings', 'STA'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geosas.fr/sofair',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'name': {
            'title': 'Nom',
            'description': 'L\'identifiant de votre instance sensorthings sans accent, ni espace ',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            'keywords': ['identifiant', 'nom']
        },
        'description': {
            'title': 'Description',
            'description': 'Description de votre instance sensorthings sans accent, ni espace ',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,  # TODO how to use?
            'keywords': ['description', 'résumé']
        },
        'author': {
            'title': 'Auteur',
            'description': 'Nom de la personne qui crée l\'instance',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['nom']
        }
    },
    'outputs': {
        'STAUrl': {
            'title': 'STAUrl',
            'description': 'l\'URL de l\'instance SensorThings créée',
            'schema': {
                'type': 'string'
            }
        }
    },
    'example': {
        'inputs': {
            'name': 'agrhys',
            'description': 'Observatoire de recherche en environnement AgrHyS',
            'author': 'Christophe Geneste'
        }
    }
}


class createSTAProcessor(BaseProcessor):
    """Create STA example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeoapi.process.createSTA.createSTAProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data):

        mimetype = 'application/json'
        name = data.get('name')
        description = data.get('description')
        author = data.get('author')

        if name is None:
            raise ProcessorExecuteError('Cannot process without a name')

        createSTA.main (name,description,author)
#        value = retour.strip()
        STAUrl = f'https://frost.geosas.fr/{name}/'.strip()

        outputs = {
            'STAUrl': STAUrl
        }

        return mimetype, outputs

    def __repr__(self):
        return f'<createSTAProcessor> {self.name}'
