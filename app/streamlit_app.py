import pandas as pd
import json 
from geopy.geocoders import Nominatim 
import numpy as np
import folium 
import streamlit as st
from streamlit_folium import folium_static

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import RendererAgg
import seaborn as sns

data_source = pd.read_csv('data/raw/publico_scraper.csv.gz', compression='gzip')
data_source.dropna(inplace=True)
GEO_DATA = json.load(open('app/georef-portugal-distrito.geojson'))

def center():
    address = 'Portugal'
    geolocator = Nominatim(user_agent="id_explorer")
    location = geolocator.geocode(address)
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

def show_maps(data, year, threshold_scale):
    data['city'] = data['city'].str.upper()
    data = data[data['year'] == year]

    map_sby = folium.Map(tiles="OpenStreetMap", location=[centers[0], centers[1]], zoom_start=7)

    maps = folium.Choropleth(
        geo_data = GEO_DATA,
        data = data[['city', 'N']],
        columns=['city', 'N'],
        key_on='feature.properties.dis_name_upper',
        threshold_scale=threshold_scale,
        fill_color='YlOrRd', 
        fill_opacity=0.3, 
        line_opacity=0.2,
        legend_name='N',
        highlight=True,
        reset=True,
        overlay=True,
        ).add_to(map_sby)

    folium.LayerControl().add_to(map_sby)
    # maps.geojson.add_child(folium.features.GeoJsonTooltip(fields=['dis_name_upper', 'N'],
    #                                                      aliases=['City: ', 'Count'],
    #                                                      labels=True))                                                       
    folium_static(map_sby)

def plot_stats(data, year):
    fig = Figure()
    ax = fig.subplots()
    df = data[data.year==year]
    sns.barplot(x=df['city'],
                y=df['N'], color='goldenrod', ax=ax)
    ax.set_xlabel('Year')
    ax.set_ylabel('Books Read')
    ax.tick_params(axis='x', rotation=90)
    st.pyplot(fig)

sns.set_style('darkgrid')
centers = center()

select_data = st.sidebar.radio(
    "Categorias",
    ("Crime", "Incendios")
)

st.header('CitySonar')

# for idx in range(31):
#     data_geo['features'][idx]['properties']['Total_Pop'] = int(data['Total Population'][idx])
#     data_geo['features'][idx]['properties']['Male_Pop'] = int(data['Male Population'][idx])
#     data_geo['features'][idx]['properties']['Female_Pop'] = int(data['Female Population'][idx])
#     data_geo['features'][idx]['properties']['Area_Region'] = float(data['Areas Region(km squared)'][idx])

year = st.slider('Ano', 2015, 2021, (2015, 2021))

subset = data_source.groupby(['city', 'year']).size().reset_index(name='N')

st.subheader('Numero de noticias por região')
show_maps(subset, year[0], threshold(subset))

st.subheader('Distribuição de artigos por jornais')
plot_stats(subset, year[0])