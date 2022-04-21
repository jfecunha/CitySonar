"""Scraper to extract data from Arquivo.pt"""
import logging
import json
import requests

from tqdm import tqdm

import pandas as pd

if __name__ == "__main__":
    logger = logging.getLogger("Arquivo-Scraper")
    logging.basicConfig(level=logging.INFO)

    cities = [
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

    max_items = 10
    from_ = 2019
    to_ = 2020
    websites = ['expresso.pt' ,'publico.pt', 'jn.pt', 'jornaldenegocios.pt', 'observador.pt']
    columns=['city', 'title', 'content', 'year', 'tstamp', 'link', 'source']

    logging.info('Initializing calls')
    data = pd.DataFrame(columns=columns)
    for city in tqdm(cities):
        logging.info('On city %s', city)
        for year in range(from_, to_):
            logging.info('On year %s', year)
            for website in websites:
            
                link = f"https://arquivo.pt/textsearch?q={city}&siteSearch={website} \
                    &maxItems={max_items}&dedupValue=1&prettyPrint=true&from={str(year)}&to={str(year+1)}"
                
                try:
                
                    r = requests.get(link)
                    payload = json.loads(r.text)
                    source = payload['request_parameters']['siteSearch'][0]
                
                    for idx, article in enumerate(payload['response_items']):

                        #time.sleep(1)
            
                        data = pd.concat([data, pd.DataFrame({
                            'city': city, 'title': article['title'], 'content': requests.get(article['linkToExtractedText']).text, 
                            'year': year, 'tstamp': article['tstamp'], 'link': article['linkToArchive'], 'source': source}, index=[idx])
                        ], ignore_index=True)
                
                except Exception as e:
                    print(e)
                    data = pd.concat([data, pd.DataFrame({
                            'city': city, 'title': None, 'content': None, 
                            'year': year, 'tstamp': None, 'link': None, 'source': None
                            }, index=[idx])
                    ], ignore_index=True)

    data.to_csv('data/scraping_data_v2.csv.gz', compression='gzip', index=False)   