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

    def split_list(self, a_list): #if array data observations trop grande
        if len(a_list) >15000:
            print("liste allégée")
            half = len(a_list)//2
            return [a_list[:half], a_list[half:]]
        return [a_list]

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


def main(chemin, colonne_date, format_date, username, password):
    print("start module")
    sessionST=instanceST("https://api.geosas.fr/wsci/v1.0/", username, password)
    get_token = sessionST.connexion() # connexion au serveur
    if get_token != True:
        return "echec logging (erreur serveur)"
    try:
        if chemin.split('.')[1] == "xlsx":
            data=pd.read_excel(chemin)  # va chercher le fichier xlsx
        else :
            data=pd.read_csv(chemin)

    except Exception as e:
        print(e)
        return "erreur fichier xlsx ou csv  vérifier format du fichier (xlsx) ou le nom des tables"
    print("ouverture fichier ok")
    print( colonne_date, format_date)
    #fonction de vérification  qui check le creation_X  et return dans api si erreur le name àprobnlème
    try:
        data[colonne_date]=pd.to_datetime(data[colonne_date], errors='raise',format=format_date)
    except:
        from pandas._libs.tslibs.parsing import guess_datetime_format
        format_date_x=guess_datetime_format(data[colonne_date].values[0])
        try:
            data[colonne_date]=pd.to_datetime(data[colonne_date], errors='raise',format=format_date_x)
        except:
            format_date_x=format_date_x.replace("%m/%d", "%d/%m")
            data[colonne_date]=pd.to_datetime(data[colonne_date], errors='raise',format=format_date_x)
            print('error date foramt')
    data[colonne_date] = data[colonne_date].apply(lambda x: x.strftime('%Y-%m-%dT%I:%M:%SZ'))
    print("conversion date ok")
    for i in data.columns:
        if i == colonne_date:
            continue
        print(i)
        dataStreamID = sessionST.getIdObjet('Datastreams', i)
        print(dataStreamID)


        exPort=data[[colonne_date,i]]
        exPort=exPort.rename(columns={colonne_date:'phenomenonTime'})
        exPort=exPort.dropna()
        exPort['resultTime']=exPort['phenomenonTime']
        exPort=exPort.rename(columns={i:"result"})

        list_data=[]
        for idx,row in exPort.iterrows():
            list_data.append([row.phenomenonTime,row.resultTime,row.result])

        list_data=sessionST.split_list(list_data)

        for chunk in list_data:
            data_set= {
                "Datastream": {
                    "@iot.id": dataStreamID
                 },
                "components": [
                    "phenomenonTime",
                    "resultTime",
                    "result"
                ],
                 "dataArray": chunk
                }

            json_data = json.dumps(data_set)

            r = requests.post(url=sessionST.urlServeur+"CreateObservations",
                              headers= {'Content-Type': 'application/json',
                                        'Authorization': "Bearer {}".format(sessionST.token)},
                              data=json_data)
            print(r.status_code)


    return "import des data terminé !"