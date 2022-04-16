"""Extract keyword sentimemt."""

import ast
import logging

from tqdm import tqdm
from typing import List

import pandas as pd
import numpy as np
import pickle
import fasttext



if __name__ == "__main__":
    
    logger = logging.getLogger("Keywords-Sentiment")
    logging.basicConfig(level=logging.INFO)

    logging.info('Loading data')
    with open('data/processed/docs_keywords.pickle', 'rb') as handle:
        docs_keywords = pickle.load(handle)

    logging.info('Loading model')
    model = fasttext.load_model('models/trained/fasttext-sentiment.bin')

    logging.info('Extracting sentiment')
    keywords_sentiment = []
    for keywords in tqdm(docs_keywords):
        temp = []
        for keyword in keywords:
            temp.append((keyword[0], model.predict(keyword[0])[0][0]))
        keywords_sentiment.append(temp)

    logging.info('Saving')
    with open("data/processed/docs_keywords_sentiment.pickle", "wb") as fp: 
        pickle.dump(keywords_sentiment, fp,  protocol=pickle.HIGHEST_PROTOCOL)
