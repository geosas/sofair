#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
# coding: utf-8

import sys
import psycopg2
import pprint
import shutil
import re
import errno
from pathlib2 import Path
import subprocess
from optparse import OptionParser
from subprocess import call
import requests
import time


#Options de connexion :
#  -h, --host=HOTE nom d'hôte du serveur de la base de données ou répertoire
#                  de la socket (par défaut : /var/run/postgresql)
#  -p, --port=PORT port du serveur de la base de données (par défaut :
#                  « 5432 »)
#  -U, --username=NOM
#                  nom d'utilisateur de la base de données (par défaut :
#                  « squivid »)
#  -W, --password  force la demande du mot de passe (devrait survenir
#                  automatiquement)


parser = OptionParser()
parser.add_option("-s", "--server", dest="host",
                  default="194.167.76.106",
                  help="Nom d'hote du serveur de la base de donnees", type="str")
parser.add_option("-i", "--instance", dest="instance",
                  default="moninstance",
                  help="Nom de l'instance STA", type="str")
parser.add_option("-p", "--port", dest="port",
                  default="5433",
                  help="Port du serveur de la base de données (par défaut :« 5433 »)", type="str")
parser.add_option("-u", "--username", dest="username",
                  default="sensorthings",
                  help="Nom d'utilisateur de la base de données (par défaut :« squivid »)", type="str")
parser.add_option("-w", "--password", dest="password",
                  default="sensorthings29",
                  help="Mot de passe", type="str")
parser.add_option("-f", "--frost_src_dir", dest="frost_src_dir",
                  default="/data/ids/war/frost/FROST-2.0.0/",
                  help="FROST source directory", type="str")
parser.add_option("-g", "--frost_dest_dir", dest="frost_dest_dir",
                  default="/data/ids/war/frost/FROST-",
                  help="FROST destination directory", type="str")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose mode")
parser.add_option("-c", "--schema", dest="schema",
                  default="public",
                  help="Schema de la base de données (par défaut :« public »)", type="str")

(options, args) = parser.parse_args()

host = options.host
port = options.port
instance = options.instance
database = "FROST"+instance
schema = options.schema
username = options.username
password = options.password
verbose = options.verbose
frost_src_dir = options.frost_src_dir
frost_dest_dir = options.frost_dest_dir

if verbose == True:
    print ("host :" + host)
    print ("port :" + port)
    print ("database :" + database)
    print ("schema :" + schema)
    print ("user :" + username)
    print ("password :" + password)

# define a function that handles and parses psycopg2 exceptions

def main (name,description,author) :
    database = "FROST"+name
    connect_db("postgres")
    create_db(database)
    connect_db(database)
    create_postgis_extension(database)
    conn.close()
    copy_frost_dir(name)
    config_frost_dir(name)
    deploy_tomcat_war (name)
    update_db(name)
    
def connect_db (db) :
    global conn
    global cursor
    options_conn = "-c search_path="+schema
    print ("options connexion db :"+db)
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=db, user=username, password=password, options=options_conn)
        conn.autocommit = True
        cursor = conn.cursor()
    except OSError as err:
        print("Error: % s" % err)

def create_db (db) :
    query_select = 'CREATE DATABASE "'+db+'";'
    print (query_select)
    cursor.execute(query_select)

def create_postgis_extension (db) :
    query_select = "CREATE EXTENSION postgis;"
    print (query_select)
    cursor.execute(query_select)

def copy_frost_dir (i) :
    dest = frost_dest_dir+i
    print ("copy "+frost_src_dir+" --> "+dest)
    try:
        shutil.copytree(frost_src_dir, dest)
    except OSError as err:
     # error caused if the source was not a directory
        if err.errno == errno.ENOTDIR:
            shutil.copy2(frost_src_dir, dest)
        else:
            print("Error: % s" % err)

def config_frost_dir (i) :
    context_file = frost_dest_dir+i+"/META-INF/context.xml"
    print (context_file)
    path = Path(context_file)
    text = path.read_text()
    text = text.replace("STAinstance", i,)
    path.write_text(text)

def deploy_tomcat_war (i) :
    instance_dir = frost_dest_dir+i
    cmd = "jar cvf "+instance_dir+".war "+instance_dir
    context_file = frost_dest_dir+i+"/META-INF/context.xml"
    print (cmd)
    # result = subprocess.run(["jar", "cvf", instance_dir+".war", instance_dir], stderr=subprocess.PIPE, text=True)
    # print(result.stderr)
    result = subprocess.run(["ln", "-s", instance_dir, "/var/lib/tomcat9-frost/webapps/"+i], stderr=subprocess.PIPE, text=True)
    print(result.stderr)

def update_db (i):
    t=15
    print ("wait "+str(t)+" sec...")
    time.sleep(t)
    url = "https://frost.geosas.fr/"+i+"/DatabaseStatus" 
    print (url)
    myobj = {'somekey': 'somevalue'}
    mydata = {'doupdate': 'Do+Update'}
    x = requests.post(url, data = mydata)
    print(x.text)

if __name__ == "__main__":
    connect_db("postgres")
    create_db(database)
    connect_db(database)
    create_postgis_extension(database)
    conn.close()
    copy_frost_dir(instance)
    config_frost_dir(instance)
    deploy_tomcat_war (instance)
    update_db(instance)

# finally:
    print ("---------------- Fin de la création de la base ----------------------")

