"""Extract articles from publico website."""

import logging
import json
import requests
import re
import time

from tqdm import tqdm

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from joblib import Parallel, delayed 

PATH = '../Projects/SmartArchive/selenium/chromedriver'


def extract_info_from_url(url, city, year):
    
    try :
        driver = webdriver.Chrome(PATH)
        driver.get(url)

        tag = driver.find_element(by=By.XPATH, value='//*[@id="story-header"]/div/div[1]')
        title = driver.find_element(by=By.XPATH, value='//*[@id="story-header"]/div/h1')
        sub_title = driver.find_element(by=By.XPATH, value='//*[@id="story-header"]/div/div[2]')
        body = driver.find_element(by=By.XPATH, value='//*[@id="story-body"]')
        main_tag = re.findall(r"(?<=\d\d\d\d/\d\d/\d\d/)\w+", url)[0]

        data = {
            'city': city ,'main_tag': main_tag, 'tag': tag.text, 
            'title': title.text, 'sub_title': sub_title.text, 'body': body.text,
            'year': year
        }
        driver.quit()
    
    except Exception as e:
        data = {
            'city': None ,'main_tag': None, 'tag': None, 
            'title': None, 'sub_title': None, 'body': None,
            'year': None
        }

    time.sleep(float(abs(np.random.normal(0, 0.1, 1))))
    return data 


if __name__ == "__main__":
    logger = logging.getLogger("Publico-Scraper")
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

    articles = []
    results = []

    logging.info('Initializing')
    for city in cities:
        logging.info('Initializing scraping process for %s.', city)
        for year in range(2015, 2023):
            logging.info('Year %s.', year)
            
            starting_date = f'01-01-{year}'
            ending_date = f'31-12-{year}'
            page_number = 0
            counter = 0
    
            while not isinstance(counter, list):
                link = f"https://www.publico.pt/api/list/search/?query={city}&start={starting_date}&end={ending_date}&page={page_number}"
                f = requests.get(link)
                content = json.loads(f.text)
                if not content:
                    counter = []
                articles.append(content)
                page_number += 1

            articles = [item for sublist in articles for item in sublist]
            
            articles_url = [f['fullUrl'] for f in articles if isinstance(f, dict)] # some files are broken

            logging.info('Number of URLs to scrap: %s.', len(articles_url))
            results.append(Parallel(n_jobs=2)(delayed(extract_info_from_url)(url, city, year) for url in articles_url))
       
    logging.info('Saving')
    results_flatten = [item for sublist in results for item in sublist]
    data = pd.DataFrame(results_flatten)
    data.to_csv('data/raw/publico_scraper.csv.gz', compression='gzip', index=False)   
    