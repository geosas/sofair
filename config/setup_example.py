#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Calculate inversion for all stations

import os



class confLoading:
    """Class with all configuration parameters.
    Load all parameters isn't a problem and only
    one function to modify if a parameter has appended.
    """

    def __init__(self):
        """Load configuration file and values

        :param cfgFile: Configuration file
        :type cfgFile: str
        :return: Values loaded
        :rtype: str
        """

        # Load configuration

        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.pathStatic=dir_path+'/static/'
        self.pathScript=dir_path+'/script/'
        self.pathData=dir_path+'/data/'

        self.url_sofair_api='https://geosas.fr/sofair-dev/api/'
        self.url_Mviewer_geosas='https://geosas.fr/mviewer-test/?config='
        self.url_sofair_static='https://geosas.fr/sofair-dev/static/'

        self.conn_string = ''
        self.service_url='https://geosas.fr/geoserver'
        self.workspace='sensorthings'
        self.name_entrepot=""
        self.auth_x=("", "")

        self.dir_xlsx=dir_path+"/static/xlsx/config_upload"
        self.dir_xlsx_data=dir_path+"/static/xlsx/data"
        self.username=""
        self.password=""