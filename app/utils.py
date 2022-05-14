"""Utility method for Streamlit APP."""
import ast
import re

import numpy as np
import folium 
import streamlit as st
import seaborn as sns
import plotly.express as px

from geopy.geocoders import Nominatim 
from matplotlib.figure import Figure
from geopy.geocoders import Nominatim 
from streamlit_folium import folium_static

CATEGORIES = (
    "Geral",
    "Politica", 
    "Cultura",
    "Economia",
    "Desporto",
    "Saude",
    "Ambiente",
    "Justica",
    "Turismo/Lazer",
    "Educacao",
    "Incendios",
    "Ciencia",
    "Crime",
    "Forças-Segurança",
    "Acidentes",
    "Transportes",
    "Sociedade",
    "Habitacao",
    "Religiao",
    "Tecnologia")   

CITIES = [
        "Geral",
        "Lisboa",
        "Porto",
        "Setúbal",
        "Braga",
        "Aveiro",
        "Faro",
        "Leiria",
        "Santarém",
        "Coimbra",
        "Viseu",
        "Viana do Castelo",
        "Vila Real",
        "Castelo Branco",
        "Évora",
        "Beja",
        "Guarda",
        "Bragança",
        "Portalegre",
    ]

def process_geodata(geo_data, subset, year, category=None):
    if not category:
        for idx, city_content in enumerate(geo_data['features']):
                if city_content['properties']['dis_name_upper'].title() in CITIES:
                    query = subset[
                        (subset.city.str.upper() == city_content['properties']['dis_name_upper']) & 
                        (subset.year == year)]['N']
                    
                    geo_data['features'][idx]['properties']['N'] = int(query.item()) if len(query) > 0 else 0
                else:
                    geo_data['features'][idx]['properties']['N'] = 0
        return geo_data

    else:

        for idx, city_content in enumerate(geo_data['features']):
                if city_content['properties']['dis_name_upper'].title() in CITIES:
                    query = subset[
                        (subset.city.str.upper() == city_content['properties']['dis_name_upper']) & 
                        (subset.year == year) &
                        (subset.category == category)
                        ]['N']
                   
                    geo_data['features'][idx]['properties']['N'] = int(query.item()) if len(query) > 0 else 0
                else:
                    geo_data['features'][idx]['properties']['N'] = 0
        return geo_data

def center(location):
    geolocator = Nominatim(user_agent="id_explorer")
    location = geolocator.geocode(location)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude

def threshold(data):
    threshold_scale = np.linspace(data['N'].min(),
                              data['N'].max(),
                              10, dtype=float)
    threshold_scale = threshold_scale.tolist() 
    threshold_scale[-1] = threshold_scale[-1]
    return threshold_scale

def draw_map(data, centers, geo_data):
    
    map_sby = folium.Map(tiles="OpenStreetMap", location=[centers[0], centers[1]], zoom_start=7)

    maps = folium.Choropleth(
        geo_data = geo_data,
        data = data[['city', 'N']],
        columns=['city', 'N'],
        key_on='feature.properties.dis_name_upper',
        threshold_scale=threshold(data),
        fill_color='YlOrRd', 
        fill_opacity=0.7, 
        line_opacity=0.2,
        legend_name='N',
        highlight=True,
        reset=True,
        overlay=True,
        ).add_to(map_sby)

    folium.LayerControl().add_to(map_sby)
    maps.geojson.add_child(folium.features.GeoJsonTooltip(fields=['dis_name_upper', 'N'],
                                                         aliases=['Cidade: ', 'Número_de_noticias'],
                                                         labels=True))                                                       
    folium_static(map_sby)

def plot_articles(data):
    try:
        fig = px.bar(data, x='N', y='source', template='seaborn', orientation='h', color='source')
        fig.update_layout(
            #title="Plot Title",
            xaxis_title="Número de registos",
            yaxis_title="Fontes",
            legend_title="Fontes",
            # font=dict(
            #     family="Courier New, monospace",
            #     size=18,
            #     color="RebeccaPurple"
            # )
        )
        st.plotly_chart(fig, use_container_width=True) 
    except Exception as e:
        print(e)
        print(data)
        st.markdown('Não há dados para a categoria selecionada')

def plot_political_parties(data, year, city):
    sns.set_style('darkgrid')
    fig = Figure()
    ax = fig.subplots()
    
    data['year_bucket'] = data['year_bucket'].apply(lambda val: ast.literal_eval(val))
    mask = data.year_bucket.apply(lambda val: year in val)
    df = data[mask]
    df = df[(df.city == city)]
    df = df.rename(columns={"%": "Percentagem", "political_party": "Partido"})

    fig = px.pie(df, values='Percentagem', names='Partido')
    fig.update_layout(legend_title="Partidos Politicos")
    st.plotly_chart(fig, use_container_width=True) 

def build_keyword_annotations(doc, keywords):
    article = []
    for word in doc.split(' '):
        #print(re.findall("[a-zA-Z]+", word))
        w = re.findall("\w+", word)
        if w: 
            if w[0] not in keywords:
                article.append(f"{word} ")
            if w[0] in keywords:
                article.append((w[0], 'keyword'))
    return article