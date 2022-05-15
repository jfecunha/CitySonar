"""Streamlit APP."""
import ast
import json

import pandas as pd 
import folium 
import streamlit as st

from streamlit_folium import folium_static
from annotated_text import annotated_text

from utils import (
    CATEGORIES,
    CITIES,
    build_keyword_annotations,
    process_geodata,
    center,
    threshold,
    draw_map,
    plot_articles,
    plot_political_parties
)
# Publico Source
publico_articles = pd.read_csv('data/processed/publico_docs_cleaned_w_keywords.csv.gz', compression='gzip')

# Arquivo Source
articles_general = pd.read_csv('data/dashboard/articles_general.csv')
subset_categories = pd.read_csv('data/dashboard/subset_categories.csv')
subset_articles_general = pd.read_csv('data/dashboard/subset_articles_general.csv')
subset_articles_categories = pd.read_csv('data/dashboard/subset_articles_categories.csv')

# Wikipedia
data_political_parties = pd.read_csv('data/scraping_political_parties.csv.gz', compression='gzip')
geo_data = json.load(open('app/georef-portugal-distrito.geojson'))


if __name__ == "__main__":

    st.set_page_config(page_title='CitySonar',  layout='wide', page_icon=':city:')

    ### Side buttons
    st.sidebar.image("images/citySonar.png", use_column_width=True)
    
    city = st.sidebar.selectbox("Escolha a cidade", CITIES) 

    category = st.sidebar.radio(
        "Categorias",
        CATEGORIES
    )

    ### Main page

    ## Page 1
    if city == 'Geral':
        st.header('Métricas')
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))
          
        m1.write('')
        m2.metric(label ='Número total de noticias extraídas',value = articles_general.N.sum())
        m3.metric(label ='Número de jornais usados',value = 4)
        m4.metric(label = 'Número de cidades analisadas',value = len(CITIES)-1)
        m1.write('')

        st.header('Visão agregada de todas as cidades')
        st.subheader('Número de noticias por região')
        year = st.slider('Ano', 2014, 2021, (2014, 2021))
        centers = center('Portugal')

        if category == 'Geral':
            st.subheader(f"Categoria: {category}")

            geo_data_p = process_geodata(geo_data, articles_general, year[0])
            articles_general['city'] = articles_general['city'].str.upper()
            query = articles_general[(articles_general['year'] == year[0])][['city', 'N']]
            draw_map(query, centers, geo_data_p)

            st.subheader('Distribuição de fontes dos artigos para todas as categorias')
            query = subset_articles_general[subset_articles_general.year == year[0]]
            query = query.groupby(['source'])['N'].sum().reset_index(name='N')
            plot_articles(query)
        else:
            st.subheader(f"Categoria: {category}")

            geo_data_p = process_geodata(geo_data, subset_categories, year[0], category)
            subset_categories['city'] = subset_categories['city'].str.upper()
            query = subset_categories[(subset_categories['year'] == year[0]) & (subset_categories['category'] == category)][['city', 'N']]
            draw_map(query, centers, geo_data_p)

            st.subheader(f'Fontes dos artigos extraidos para a categoria selectionada')
            query = subset_articles_categories[
                (subset_articles_categories.category == category) &
                (subset_articles_categories.year == year[0])
                ]
            query = query.groupby(['source'])['N'].sum().reset_index(name='N')
            plot_articles(query)
    ## Page 2
    else:
        st.subheader(f'{city}')
        year = st.slider('Ano', 2014, 2021, (2014, 2021))
        centers = center(city)
        subset_categories['city'] = subset_categories['city'].str.upper()
        query = subset_categories[(subset_categories['year'] == year[0]) & (subset_categories['category'] == category)][['city', 'N']]

        st.subheader(f"Categoria: {category}")
        map_sby = folium.Map(tiles="OpenStreetMap", location=[centers[0], centers[1]], zoom_start=8)
        geo_data_slice = [c for c in geo_data['features'] if c['properties']['dis_name'] == city]
        geo_data['features'] = geo_data_slice
        
        maps = folium.Choropleth(
            geo_data = geo_data,
            data = query[['city', 'N']],
            columns=['city', 'N'],
            key_on='feature.properties.dis_name_upper',
            threshold_scale=threshold(query),
            fill_color='YlOrRd', 
            fill_opacity=0.7, 
            line_opacity=0.2,
            legend_name='N',
            highlight=True,
            reset=True,
            overlay=True,
            ).add_to(map_sby)
        folium_static(map_sby)

        if category == 'Geral':
            st.subheader(f'Fontes dos artigos extraídos para todas as categorias')
            query = subset_articles_general[
                (subset_articles_general.year == year[0]) & (subset_articles_general.city == city)]
            plot_articles(query)
        else:

            articles = publico_articles[
            (publico_articles.category == category) & 
            (publico_articles.city == city) &
            (publico_articles.year == year[0])
            ]
            st.subheader(f'Notícias')
            #articles_query = articles.sample(n=10 if len(articles) > 10 else len(articles), replace=False)
            n = 10 if len(articles) > 10 else len(articles)
            articles_query = articles.iloc[0:n]

            #st.dataframe(articles_query[['title', 'category', 'year', 'keywords']])

            st.selectbox("Escolha a notícia", tuple(articles_query.title.tolist()), key='news')#, on_change=form_callback)
            title = st.session_state.news
            st.markdown('**Palavras-Chave**')
            try:
                keywords = ast.literal_eval(articles_query[articles_query.title==title].keywords.item())
                keywords = [k.split(' ') for k in keywords]
                keywords = [item for sublist in keywords for item in sublist]
                articles_to_display = articles_query[articles_query.title==title].body.item()
                annotated_text(*build_keyword_annotations(articles_to_display, keywords))
                
            except ValueError:
                st.markdown('Não há dados disponíveis.')
                articles_to_display = []

            st.write('')    
            st.subheader(f'Fontes dos artigos extraídos para a categoria selecionada')
            query = subset_articles_categories[
                (subset_articles_categories.category == category) & 
                (subset_articles_categories.city == city) &
                (subset_articles_categories.year == year[0])
                ]
            if not articles_to_display:    
                plot_articles(articles_to_display)
            else:
                plot_articles(query)

        st.subheader(f'Composição partidária da cidade')
        plot_political_parties(data_political_parties, year[0], city)
        st.markdown(f'Dados extraidos de: https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%B5es_legislativas_portuguesas_de_{year[0]}')
        st.markdown('**Portugal à frente**: Coligação eleitoral entre PPD/PSD e CDS-PP')
        st.markdown('**Coligação Democrática Unitária**: Coligação eleitoral entre PCP e PEV')




