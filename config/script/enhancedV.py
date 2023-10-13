# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 11:52:31 2021

@author: tloree
"""
import requests
import pandas as pd
import plotly.graph_objects as go
import logging
from pandas._libs.tslibs.parsing import guess_datetime_format

def q25(x):
    return x.quantile(0.25)

def q50(x):
    return x.quantile(0.50)

# 75th Percentile
def q75(x):
    return x.quantile(0.75)


def main(url_sensorthings, year_etude, idprocess, config):

    logging.basicConfig(filename=config.pathData+"logger.log", encoding='utf-8', level=logging.DEBUG)
    logging.info("requests ST ")
    #try:
    r=requests.get(url_sensorthings+"/Observations?$top=1000&$select=result,phenomenonTime")
    first=r.json()['value']
    while '@iot.nextLink' in r.json():
        r=requests.get(r.json()['@iot.nextLink'])
        first+=r.json()['value']
    df=pd.DataFrame(first)
    logging.info("requests ST ok df open")

    r=requests.get(url_sensorthings+"?$select=name,unitOfMeasurement,description")
    unite_name=r.json()['unitOfMeasurement']['name']
    datas_name=r.json()['name']
    datas_description=r.json()['description']

    try:
        logging.info("essaye format basique")
        df['phenomenonTime']=pd.to_datetime(df['phenomenonTime'],format='%Y-%m-%dT%H:%M:%S%fZ')
    except:
        logging.info("erreur format basique")
        try:
            logging.info("essaye guess format basique")
            format_date_x=guess_datetime_format(df['phenomenonTime'].values[0])
            df['phenomenonTime']=pd.to_datetime(df['phenomenonTime'],format=format_date_x,utc=True)
            logging.info("ok format")
            logging.info(df['phenomenonTime'].values[0])
        except:
            logging.info("essaye guess format basique 2")
            format_date_x=format_date_x.replace("%m/%d", "%d/%m")
            df['phenomenonTime']=pd.to_datetime(df['phenomenonTime'],format=format_date_x,utc=True)

    df['month']=df['phenomenonTime'].dt.strftime('%b')
    df['mois']=df['phenomenonTime'].dt.month
    df['year']=df.phenomenonTime.dt.year
    logging.info("extraction info date ok")
    df_25=df.groupby(by=['month','mois'],as_index=False).agg(q25)
    df_25=df_25.sort_values(by='mois')
    logging.info("aggreg 25 ok")
    df_median=df.groupby(by=['month','mois'],as_index=False).agg(q50)
    df_median=df_median.sort_values(by='mois')
    logging.info("median ok")
    df_75=df.groupby(by=['month','mois'],as_index=False).agg(q75)
    df_75=df_75.sort_values(by='mois')
    logging.info("aggreg 75 ok")

    df_etude=df[df.year==year_etude].groupby(by=['month','mois'],as_index=False).agg(q50)
    df_etude=df_etude.reset_index(drop=True) #bug ou version pandas ?
    df_etude=df_etude.sort_values(by='mois')

    logging.info("stat ok start figure")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(df_25.month.values) + list(df_75.month[::-1].values),
        y=list(df_25.result.values) + list(df_75.result[::-1].values),
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line_color='rgba(255,255,255,0)',
        name='Intervalle q25-75',
    ))
    fig.add_trace(go.Scatter(
        x=df_median.month,
        y=df_median.result,
        line_color='rgb(0,100,80)',
        name='mediane interannuelle'
    ))

    fig.add_trace(go.Scatter(
        x=df_etude.month,
        y=df_etude.result,
        line_color='rgb(0,176,246)',
        name='mediane'
    ))

    fig.update_traces(mode='lines')

    fig.update_layout(title='Aggrégation pour l\'année %s du datastreams %s %s' % (year_etude,datas_name,datas_description),
                    xaxis_title='Mois',
                    yaxis_title=unite_name)

    url_plot=config.pathStatic+"tmp/"+idprocess+".html"
    logging.info("write figure")
    fig.write_html(url_plot,auto_open=False)
    url_plot=config.url_sofair_static+"tmp/"+idprocess+".html"
    #except Exception as e:
    #    print(e)
    #    f = open("/usr/local/sofair-dev/config/data/log.txt", "a")
     #   f.write(str(e))
    #    f.close()
     #   url_plot='failed'
    #    return url_plot

    return url_plot