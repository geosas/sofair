from flask import Blueprint, render_template, request, jsonify
import json
from werkzeug.utils import secure_filename
import os
import requests
import json
from time import sleep
from setup import confLoading
config = confLoading()

ALLOWED_EXTENSIONS =  {'xlsx','csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    page d'accueil

    :returns: template
    """
    print("connexion SOFair index")
    statJsonST = {
        "nb_instances": 0,
        "nb_things": 0,
        "nb_observedProperties": 0,
        "nb_observations": 0
    }
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']
    statJsonST ['nb_instances'] = len (baseJsonST)
    for i in baseJsonST:
        statJsonST ['nb_things'] += i['nb_things']
        statJsonST ['nb_observedProperties'] += i['nb_observedProperties']
        statJsonST ['nb_observations'] += i['nb_observations']

    with open(confLoading().pathStatic+"json/dico_jinja.json",'r', encoding='utf-8') as dico_template:
        dict_metadata=json.load( dico_template)

    return render_template('index.html',baseJsonST= baseJsonST, dict_metadata = dict_metadata, statJsonST = statJsonST)


@main.route('/home')
def home():
    """
    page d'accueil

    :returns: template
    """
    print("connexion SOFair index")
    statJsonST = {
        "nb_instances": 0,
        "nb_things": 0,
        "nb_observedProperties": 0,
        "nb_observations": 0
    }
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']
    statJsonST ['nb_instances'] = len (baseJsonST)
    for i in baseJsonST:
        statJsonST ['nb_things'] += i['nb_things']
        statJsonST ['nb_observedProperties'] += i['nb_observedProperties']
        statJsonST ['nb_observations'] += i['nb_observations']

    with open(confLoading().pathStatic+"json/dico_jinja.json",'r', encoding='utf-8') as dico_template:
        dict_metadata=json.load( dico_template)

    return render_template('index.html',baseJsonST= baseJsonST, dict_metadata = dict_metadata, statJsonST = statJsonST)

@main.route('/creation-instance')
def instance():
    """
    page creation instance

    :returns: template
    """
    print("connexion creation-instance")
    return render_template('creationInstance.html')

@main.route('/configure')
def configure():
    """
    page config

    :returns: template
    """
    print("connexion configure")
    return render_template('creationInstance.html')

@main.route('/publication')
def publication():
    """
    page publication

    :returns: template
    """
    print("connexion publication")
    return render_template('creationInstance.html')

@main.route('/ids')
def ids():
    """
    page ids

    :returns: template
    """
    print("connexion ids")
    return render_template('creationInstance.html')

@main.route('/viewer')
def viewer():
    """
    page viewer

    :returns: template
    """
    print("connexion viewer")
    return render_template('creationInstance.html')

@main.route('/STARecords')
def STARecords():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche STARecords")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']
    return render_template('STARecords.html',baseJsonST= baseJsonST)

@main.route('/create-instance')
def createinstance():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche create-instance")
    with open(confLoading().pathStatic+"json/STAServices.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseAPIServices = json.load(json_src)
    baseAPIServices=baseAPIServices['STAServices']

    return render_template('create-instance.html',baseAPIServices= baseAPIServices)

@main.route('/configure-instance-tom')
def createinstancetom():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche create-instance-tom")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']

    return render_template('configure-instance-tom.html',baseJsonST= baseJsonST)

@main.route('/upload_config', methods=['POST'])
def upload_config():
    print('fichier recu check en cours')
    #récupère le fichier config xlsx et l'envoie l'appel de l'api sofair de création de config
    if 'file' not in request.files:
        return jsonify({"etat":"erreur","texte":"pas de fichier envoyé (erreur 1)"})
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({"etat":"erreur","texte":"pas de fichier envoyé (erreur 2)"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(confLoading().pathStatic+"xlsx/config_upload", filename))
    print('check ok fichier save')
    json_data = json.dumps({
        "inputs":{
            "config_xlsx":filename
        },"mode": "async","response":"document"
    })
    print('post api ')
    r=requests.post(url=config.url_sofair_api+'processes/create-config-xlsx/execution',
        headers= {'Content-Type': 'application/json'},data=json_data)
    if r.status_code in [200,201]:
        print('post api ok en cours de trt')
        location_I=r.headers['Location']+"?f=json"
        location_R=r.headers['Location']+"/results?f=json"

        r=requests.get(url=location_I)
        if r.json()['status'] == 'failed':
            return jsonify( {"etat":"erreur", "api_response":r.json()})


        z=0
        while r.json()['progress'] != 100:
            r=requests.get(url=location_I)
            sleep(4)
            z+=1
            if z==10:
                break

        if r.json()['progress'] == 100:
            r=requests.get(url=location_R)
            print('trt fini')
            print(r.json()['response'])

            if r.json()['response'] == 'création terminée !':
                return jsonify({"etat":"ok", "api_response":r.json()})
            else:
                return jsonify({"etat":"erreur", "api_response":r.json()})
        else:
            return jsonify({"etat":"erreur", "api_response":r.json()})



@main.route('/configure-instance')
def configureinstance():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche configure-instance")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']

    with open(confLoading().pathStatic+"json/configExamples.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        configExamples = json.load(json_src)
    configExamples=configExamples['examples']

    return render_template('configure-instance.html',configExamples = configExamples,baseJsonST= baseJsonST)

@main.route('/upload-data')
def uploaddata():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche upload-data")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']

    with open(confLoading().pathStatic+"json/dataExamples.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        dataExamples = json.load(json_src)
    dataExamples=dataExamples['examples']

    return render_template('upload-data.html',dataExamples = dataExamples,baseJsonST= baseJsonST)

@main.route('/upload_data_file', methods=['POST'])
def upload_data_file():

    print('fichier recu check en cours')
    #récupère le fichier config xlsx et l'envoie l'appel de l'api sofair de création de config
    if 'file' not in request.files:
        return jsonify({"etat":"erreur","texte":"pas de fichier envoyé (erreur 1)"})
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({"etat":"erreur","texte":"pas de fichier envoyé (erreur 2)"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(confLoading().pathStatic+"xlsx/data", filename))
    print('check ok fichier save')
    print(file.filename)



    json_data = json.dumps({
        "inputs":{
            "data_file":filename,
            "mode":'large',
            "colonne_date": "date",
            "format_date": "%Y%m%d",

        },"mode": "async","response":"document"
    })

    print('post api ')
    r=requests.post(url=config.url_sofair_api+'processes/post-observations/execution',
        headers= {'Content-Type': 'application/json'},data=json_data)

    if r.status_code in [200,201]:
        print('post api ok en cours de trt')
        location_I=r.headers['Location']+"?f=json"
        location_R=r.headers['Location']+"/results?f=json"

        r=requests.get(url=location_I)
        if r.json()['status'] == 'failed':
            return jsonify( {"etat":"erreur", "api_response":r.json()})


        z=0
        while r.json()['progress'] != 100:
            r=requests.get(url=location_I)
            sleep(4)
            z+=1
            if z==10:
                break

        if r.json()['progress'] == 100:
            r=requests.get(url=location_R)
            print('trt fini')
            print(r.json()['response'])

            if r.json()['response'] == 'import des data terminé !':
                return jsonify({"etat":"ok", "api_response":r.json()})
            else:
                return jsonify({"etat":"erreur", "api_response":r.json()})
        else:
            return jsonify({"etat":"erreur", "api_response":r.json()})


@main.route('/create-metadata-and-layer')
def createmetadata():
    """
    Fiche sta

    :returns: template
    """
    print("Fiche create-metadata-and-layer")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']

    return render_template('create-metadata-and-layer.html',baseJsonST= baseJsonST)

@main.route('/create-viewer')
def createviewer():
    """
    Fiche sta

    :returns: template
    """
    print("Page create-viewer")
    with open(confLoading().pathStatic+"json/STAInstances.json", encoding='utf-8') as json_src: #mettre dans la config le chemin
        baseJsonST = json.load(json_src)
    baseJsonST=baseJsonST['instances']

    return render_template('create-viewer.html',baseJsonST= baseJsonST)
