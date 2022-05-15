"""Scraper to extract data from Arquivo.pt"""
import logging
import json
import requests
import asyncio
import time

from typing import Dict
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

import pandas as pd


async def make_request_to_url(url):
    request = requests.get(url)
    return request

async def get_request_payload(url):
    request = await make_request_to_url(url)
    #await asyncio.sleep(5)
    try:
        payload = json.loads(request.text)
        return payload
    except Exception as e:
        print(request.text)
    

def extract_article_metadata(article: Dict, city: str, year: str, source: str):

    try:
                
        article_metadata = {
            'city': city, 'title': article['title'], 'content': requests.get(article['linkToExtractedText']).text, 
            'year': year, 'tstamp': article['tstamp'], 'link': article['linkToArchive'], 'source': source
        }

        time.sleep(1)

        return article_metadata

    except Exception as e:
        print(e)
        article_metadata = {
            'city': city, 'title': None, 'content': None, 
            'year': year, 'tstamp': None, 'link': None, 'source': None
        }

        return article_metadata


async def get_article_metadata(loop: asyncio, requests: Dict, city: str, year: str, source: str):
    executor = ProcessPoolExecutor(max_workers=4)
    article_metadata = await asyncio.gather(*(loop.run_in_executor(executor, extract_article_metadata, article, city, year, source) 
                                  for article in requests))
    return article_metadata
   

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

    max_items = 2000
    from_ = 2010
    to_ = 2023
    websites = ['expresso.pt' ,'publico.pt', 'jn.pt', 'jornaldenegocios.pt', 'observador.pt']
    columns=['city', 'title', 'content', 'year', 'tstamp', 'link', 'source']

    logging.info('Initializing calls')
    results = []    
    for city in tqdm(cities[0:]):
        logging.info('On city: %s', city)
        for year in range(from_, to_):
            logging.info('On year: %s', year)
            for website in websites:
                logging.info('On website: %s', website)
            
                link = f"https://arquivo.pt/textsearch?q={city}&siteSearch={website} \
                    &maxItems={max_items}&dedupValue=1&prettyPrint=true&from={str(year)}&to={str(year+1)}"
                
                try:
                
                    payload = asyncio.run(get_request_payload(link))
                    source = payload['request_parameters']['siteSearch'][0]
                    logging.info('Number of articles: %s', len(payload['response_items']))
                    
                    if payload['response_items']:

                        loop = asyncio.new_event_loop()
                        results.append(loop.run_until_complete(get_article_metadata(loop, payload['response_items'], city, year, source)))
                        loop.close()
                
                except Exception as e:
                    logging.info('Failed with error: %s', str(e))
                    continue

    results_flatten = [item for sublist in results for item in sublist]
    data = pd.DataFrame(results_flatten)
    data.to_csv('data/scraping_data_v2.csv.gz', compression='gzip', index=False)   
