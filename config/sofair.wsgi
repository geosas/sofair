import os
from flask import Flask
import sys

os.environ['PYGEOAPI_CONFIG'] = '/usr/local/sofair-dev/config/sofair-config.yml'
os.environ['PYGEOAPI_OPENAPI'] = '/usr/local/sofair-dev/config/sofair-openapi.yml'

sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
from pygeoapi.flask_app import BLUEPRINT as pygeoapi_blueprint
from mainPage import main as main_blueprint


application = Flask(__name__)


application.register_blueprint(pygeoapi_blueprint,url_prefix='/api')
application.register_blueprint(main_blueprint, url_prefix='/')

