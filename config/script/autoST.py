#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd  # nécessites les librairies  openpyxl, xlrd pour ouvrir le xlsx
pd.options.mode.chained_assignment = None  # default='warn'


class instanceST():
    def __init__(self, urlServeur, username, password):
        self.urlServeur = urlServeur
        self.username = username
        self.password =  password
        self.dico_bug_post_obs = {"name_thing":[],"id_thing":[],"name_datastream":[],"id_datastream":[]}
    def connexion(self):
        print("connexion", self.username, "to ",self.urlServeur)
        json_data = json.dumps({"username":self.username,"password":self.password})
        r=requests.post(url="https://api.geosas.fr/wsci/v1.0/login",
                headers= {'Content-Type': 'application/json'}, data=json_data)
        print(r.status_code)
        if r.status_code != 200:
            return False
        self.token=r.json()['token']
        return True

    def log_out(self):
        r=requests.get(url="https://api.geosas.fr/sensorthings/v1.0/logout")
        print(r.status_code)
        print(r.text)

    def post_data_serveur(self, objet, data):
        print('post Data')
        for i in data:
            self.test_json=i
            json_data = json.dumps(i)
            lien="%s/%s" % (self.urlServeur,objet)
            r = requests.post(url=lien,
                headers= {'Content-Type': 'application/json',
                          'Authorization': "Bearer {}".format(self.token)}, data=json_data)
            print(r.status_code)
            if r.status_code!= 201:
                print("error")
                print(r.text)
                try:
                    return i['name']
                except:#
                    break
        return True



    def get_data(self,url_x):
        print("get Data")
        df_all=pd.DataFrame()
        r=requests.get(url=url_x)
        data=r.json()
        df_all=df_all.append(pd.DataFrame(data['value']))
        while '@iot.nextLink' in data:
            print("next link")
            r=requests.get(url=data['@iot.nextLink'])
            data=r.json()
            df_all=df_all.append(pd.DataFrame(data['value']))
        return df_all

    def coord_lister(self, geom): #if polygon in geopandas
        coords = list(geom.exterior.coords)
        return (coords)

    def split_list(self, a_list): #if array data observations trop grande
        if len(a_list) >15000:
            print("liste allégée")
            half = len(a_list)//2
            return [a_list[:half], a_list[half:]]
        return [a_list]

    def addTableConfig(self,chemin):
        print("open xlsx table")
        self.cheminXlsx = chemin
        self.dataStreamSrc = pd.read_excel(self.cheminXlsx, sheet_name="1_datastream").drop_duplicates("name")
        self.variableName = self.dataStreamSrc['name'].unique()
        print("xlsx ok !")

    def checkDoublon(self, name, objet):
        #get name
        print("check if exist", objet)
        objetValue = self.get_data(self.urlServeur+ objet)
        if len(objetValue) == 0:
            print("Table vierge pour", objet)
            return name
        else:
            objetNew = [x for x in name if x not in objetValue['name'].values]
            objetOk = [x for x in name if x in objetValue['name'].values]
            print(objet, 'déjà publié :',objetOk,"\n")
            print(objet, 'nouveau :',objetNew)
            return objetNew

    def getIdObjet(self, objet, name):
        print("recherche id de :", objet, name)
        r=requests.get(url="%s%s?$filter=name eq '%s'"% (self.urlServeur, objet, name))
        print(r.status_code)
        objet_json=r.json()['value']
        if len(objet_json) != 1:
            print("l'objet", objet, name," n'a pas pu être trouvé")
            return -1
        else:
            print("id :",objet_json[0]['@iot.id'])
            return objet_json[0]['@iot.id']

    def creationSensor(self):
        print("publication des sensors")
        sensorSrc = pd.read_excel(self.cheminXlsx,sheet_name="3_sensor")
        sensorSrc = sensorSrc[sensorSrc['datastream name'].isin(self.variableName)]
        self.sensorName = sensorSrc['name'].unique()
        sensorSrc = sensorSrc.drop_duplicates("name")

        sensorUnique = self.checkDoublon(sensorSrc['name'].values,"Sensors")
        if len(sensorUnique)==0:
            print("pas de nouveau Sensor à publier")
            return True
        sensorSrc = sensorSrc[sensorSrc['name'].isin(sensorUnique)]
        sensorSrc = sensorSrc.fillna("")
        Sensor = []
        for idx,row in sensorSrc.iterrows():
            print(row['name'])
            Sensor.append({
				"name": row['name'],
				"description": row['description'],
				"encodingType": row['encodingType (html ou pdf)'],
				"metadata": row['metadata (lien vers description fabricant)']
			})
        return self.post_data_serveur("Sensors",Sensor)

    def creationObservedProperties(self):
        print("publication des observed properties")
        obspSrc = pd.read_excel(self.cheminXlsx,sheet_name="2_observedProperty")
        obspSrc = obspSrc[obspSrc['datastream name'].isin(self.variableName)]
        self.obspName = obspSrc['name'].unique()
        obspSrc = obspSrc.drop_duplicates("name")

        obspUnique = self.checkDoublon(obspSrc['name'].values,"ObservedProperties")
        if len(obspUnique)==0:
            print("pas de nouveau ObsP à publier")
            return True
        obspSrc = obspSrc[obspSrc['name'].isin(obspUnique)]
        obspSrc = obspSrc.fillna("")
        obsp = []
        for idx,row in obspSrc.iterrows():
            print(row['name'])
            obsp.append({
				"name": row['name'],
				"description": row['description'],
				"definition": row['definition']
			})
        return self.post_data_serveur("ObservedProperties",obsp)

    def creationThings(self):
        print("publication des things")
        thingSrc = pd.read_excel(self.cheminXlsx,sheet_name="4_thing")
        thingSrc = thingSrc[thingSrc['datastream name'].isin(self.variableName)]
        self.thingName = thingSrc['name'].unique()
        thingSrc = thingSrc.drop_duplicates("name")

        thingSrcUnique = self.checkDoublon(thingSrc['name'].values,"Things")
        if len(thingSrcUnique)==0:
           print("pas de nouveau Things à publier")
           return True
        thingSrc = thingSrc[thingSrc['name'].isin(thingSrcUnique)]

        locationSrc = pd.read_excel(self.cheminXlsx,sheet_name="5_location")
        listProperties = thingSrc.columns[~thingSrc.columns.isin(['datastream name', 'name', 'description'])]

        thingSrc = thingSrc.fillna("")
        locationSrc = locationSrc.fillna("")

        thing = []
        for idx,row in thingSrc.iterrows():
            location_thing = locationSrc[locationSrc.thing_name == row['name']]
            propertiesThing={}
            print(row['name'])
            for i in listProperties:
                print("properties",i)
                propertiesThing[i] = row[i]
            thing.append({
                "name": row['name'],
                "description": row['description'],
            	"properties": propertiesThing,
            	"Locations": [
            		{
            			"name": location_thing['name'].values[0],
            			"description":  location_thing['description'].values[0],
            			"encodingType": "application/geo+json",
            			"location": {
                            "type": "Feature",
                            "geometry": {
                                "type": location_thing['type'].values[0],
                                "coordinates": [location_thing['coordinates (X)'].values[0], location_thing['coordinates (Y)'].values[0]]
                            },
            			}
            		}
            	]
            })

        return self.post_data_serveur("Things",thing)

    def creationDataStreams(self):
        print("publication des datastreams")

        self.dataStreamName = self.dataStreamSrc['name'].unique()
        self.variableName

        dataStreamUnique = self.checkDoublon(self.dataStreamSrc['name'].values,"Datastreams")
        if len(dataStreamUnique)==0:
            print("pas de nouveau Datastreams à publier")
            return True
        self.dataStreamSrc = self.dataStreamSrc[self.dataStreamSrc['name'].isin(dataStreamUnique)]

        datastream = []
        thingSrc = pd.read_excel(self.cheminXlsx,sheet_name="4_thing")
        sensorSrc = pd.read_excel(self.cheminXlsx,sheet_name="3_sensor")
        obspSrc = pd.read_excel(self.cheminXlsx,sheet_name="2_observedProperty")

        self.dataStreamSrc = self.dataStreamSrc.fillna("")

        for idx,row in self.dataStreamSrc.iterrows():
            print(row['name'])

            idSensor = self.getIdObjet("Sensors",sensorSrc[sensorSrc['datastream name'] == row['name']]['name'].values[0])
            idObsp = self.getIdObjet("ObservedProperties",obspSrc[obspSrc['datastream name']  == row['name']]['name'].values[0])
            idThing = self.getIdObjet("Things",thingSrc[thingSrc['datastream name']  == row['name']]['name'].values[0])
            if (idSensor == -1 or idObsp == -1 or idThing == -1):
                break
            datastream.append({
    			"name": row['name'],
    			"description": row['description'],
    			"observationType": row["observationType"],
    			"unitOfMeasurement": {
    				"name": row['name'],
    				"symbol": row['symbol'],
    				"definition": row['definition']
    			},
    			"Sensor": {"@iot.id": idSensor },
    			"ObservedProperty": {"@iot.id": idObsp },
                "Thing": {"@iot.id": idThing }
            })
        return self.post_data_serveur("Datastreams",datastream)

    def postObservation_par_thing_name(self,data_obs_csv):

        print("post des observations par thing name")
        data=self.get_data(self.urlServeur+"Things?$select=name,id&$expand=Datastreams($select=name,id)")
        if len(self.dico_bug_post_obs['name_thing'])==0:
            for idx,row in data.iterrows():
                print(row['name'])
                inter=data_obs_csv[data_obs_csv.GRID_NO==int(row['name'])]
                if len(inter)==0:
                    continue
                for i in row['Datastreams']:
                    print(i['name'],i['@iot.id'])

                    exPort=inter[['date',i['name']]]
                    exPort.date=pd.to_datetime(exPort.date, errors='raise',format='%Y%m%d')
                    exPort.date = exPort.date.apply(lambda x: x.strftime('%Y-%m-%dT%H:%M:%SZ'))
                    exPort=exPort.rename(columns={'date':'phenomenonTime'})
                    #exPort=exPort.replace("NAN",np.nan)
                    exPort=exPort.dropna()
                    exPort['resultTime']=exPort['phenomenonTime']
                    exPort= exPort.rename(columns={i['name']:"result"})

                    exPort['phenomenonTime'] = exPort.phenomenonTime.map(lambda x: [x])
                    exPort['resultTime'] = exPort.resultTime.map(lambda x: [x])
                    exPort['result'] = exPort.result.map(lambda x: [x])
                    self.AAAAA=exPort
                    exPort = exPort[["phenomenonTime","resultTime","result"]]
                    list_data=list(exPort.sum(1)) #une liste évite les problème d'encoding de json.dumps qui ce bloque si le int est un np.int64
                    list_data=self.split_list(list_data)

                    for chunk in list_data:

                        data_set= {
                            "Datastream": {
                                "@iot.id": i['@iot.id']
                             },
                            "components": [
                                "phenomenonTime",
                                "resultTime",
                                "result"
                            ],
                             "dataArray": chunk
                            }

                        json_data = json.dumps(data_set)
                        r = requests.post(url=self.urlServeur+"CreateObservations",
                                          headers= {'Content-Type': 'application/json',
                                                    'Authorization': "Bearer {}".format(self.token)},
                                          data=json_data)
                        print(r.status_code)
                        if r.status_code not in [200,201]:
                            print("blocage")
                            print(r.text)
                            print(row['name'],row['name'],i['name'],i['@iot.id'])
                            self.dico_bug_post_obs["name_thing"].append(row['name'])
                            self.dico_bug_post_obs["id_thing"].append(row['@iot.id'])
                            self.dico_bug_post_obs["name_datastream"].append(i['name'])
                            self.dico_bug_post_obs["id_datastream"].append(i['@iot.id'])
                        else:
                            print('creation ok')
                            print(r.text)

        else:
            print('le dico de bug possède des things, il faut post avec une autre fonction')

    def postObservation_par_thing_name_bug(self,data_obs_csv):

        print("post des observations par thing name big")
        if len(self.dico_bug_post_obs['name_thing'])>0:
            for z in range(0,len(self.dico_bug_post_obs["name_thing"])):
                print(self.dico_bug_post_obs["name_thing"][z],self.dico_bug_post_obs["id_thing"][z])
                inter=data_obs_csv[data_obs_csv.GRID_NO==int(self.dico_bug_post_obs["name_thing"][z])]
                if len(inter)==0:
                    continue
                exPort=inter[['date',self.dico_bug_post_obs["name_datastream"][z]]]
                exPort.date=pd.to_datetime(exPort.date, errors='raise',format='%Y%m%d')
                exPort.date = exPort.date.apply(lambda x: x.strftime('%Y-%m-%dT%H:%M:%SZ'))
                exPort=exPort.rename(columns={'date':'phenomenonTime'})
                #exPort=exPort.replace("NAN",np.nan)
                exPort=exPort.dropna()
                exPort['resultTime']=exPort['phenomenonTime']
                exPort= exPort.rename(columns={self.dico_bug_post_obs["name_datastream"][z]:"result"})

                exPort['phenomenonTime'] = exPort.phenomenonTime.map(lambda x: [x])
                exPort['resultTime'] = exPort.resultTime.map(lambda x: [x])
                exPort['result'] = exPort.result.map(lambda x: [x])
                exPort = exPort[["phenomenonTime","resultTime","result"]]
                list_data=list(exPort.sum(1))

                list_data=self.split_list(list_data)

                for chunk in list_data:

                    data_set= {
                        "Datastream": {
                            "@iot.id": self.dico_bug_post_obs["id_datastream"][z]
                         },
                        "components": [
                            "phenomenonTime",
                            "resultTime",
                            "result"
                        ],
                         "dataArray": chunk
                        }

                    json_data = json.dumps(data_set)
                    r = requests.post(url=self.urlServeur+"CreateObservations",
                                      headers= {'Content-Type': 'application/json',
                                                'Authorization': "Bearer {}".format(self.token)},
                                      data=json_data)
                    print(r.status_code)
                if r.status_code not in [200,201]:
                    print("blocage")
                    print(r.text)
                    print(self.dico_bug_post_obs["name_thing"][z],
                          self.dico_bug_post_obs["id_thing"][z],
                          self.dico_bug_post_obs["name_datastream"][z],
                          self.dico_bug_post_obs["id_datastream"][z])
                else:

                    print('creation ok')
                    self.dico_bug_post_obs["name_thing"].pop(z),
                    self.dico_bug_post_obs["id_thing"].pop(z),
                    self.dico_bug_post_obs["name_datastream"].pop(z),
                    self.dico_bug_post_obs["id_datastream"].pop(z)

        else:
            print('le dico de bug ne possède de thing')


def main(chemin, username, password):
    print("start module")
    sessionST=instanceST("https://api.geosas.fr/wsci/v1.0/", username, password)
    get_token = sessionST.connexion() # connexion au serveur
    if get_token != True:
        return "echec logging (erreur serveur)"
    try:
        sessionST.addTableConfig(chemin) # va chercher le fichier xlsx
    except Exception as e:
        print(e)
        return "erreur fichier xlsx  vérifier format du fichier (xlsx) ou le nom des tables"
    #fonction de vérification  qui check le creation_X  et return dans api si erreur le name àprobnlème

    creation_Sensor = sessionST.creationSensor() #creation des Sensors avec vérification des doublons, fonction indépendante
    if creation_Sensor != True:
        return "erreur bloquante dans le fichier pour le Sensor " + creation_Sensor
    creation_ObservedProperties = sessionST.creationObservedProperties() #creation des Observed Properties avec vérification des doublons, fonction indépendante
    if creation_ObservedProperties != True:
        return "erreur bloquante dans le fichier pour le ObservedProperties " +  creation_ObservedProperties
    creation_Things = sessionST.creationThings() #creation des things + locations associées avec vérification des doublons (pour les things), fonction indépendante
    if creation_Sensor != True:
        return "erreur bloquante dans le fichier pour le Things " + creation_Things
    creation_DataStreams = sessionST.creationDataStreams() #creation des datastreams, il faut avoir déjà créé les Sensor + ObsP + Things
    if creation_Sensor != True:
        return "erreur bloquante dans le fichier pour le DataStreams " + creation_DataStreams
    sessionST.log_out()

    return "création terminée !"