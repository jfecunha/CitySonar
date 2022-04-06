import logging

from tqdm import tqdm

import numpy as np
import pandas as pd
import spacy

from nlpiper.core import Compose
from nlpiper.transformers import cleaners
from nlpiper.core import Document

from src.cleaners import TextCleaner
from resources.stopwords import WORDS

def process_stop_words():
    """Prepare stop words."""
    stop_words = Document(WORDS)
    stop_words = pipeline(stop_words)
    stop_words = stop_words.cleaned.split(' ')
    stop_words = list(filter(None, stop_words))
    return stop_words


if __name__ == "__main__":
    logger = logging.getLogger("Data-Prep")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    data = pd.read_csv('data/scraping_data.csv.gz', compression='gzip')

    logger.info('Remove Nan')
    data.dropna(inplace=True)

    pipeline = Compose([
        cleaners.CleanURL(),
        cleaners.CleanEOF(),
        cleaners.CleanMarkup(),
        cleaners.CleanAccents(),
        cleaners.CleanNumber()
    ])

    model= spacy.load("pt_core_news_lg")
    tc = TextCleaner(model=model, stop_words=process_stop_words())

    logger.info('Applying cleaning')
    processed_docs = []
    for _, val in tqdm(data.iterrows()):
        doc = Document(val['content'].lower())
        doc_p = pipeline(doc)
        doc_p = tc(doc_p.cleaned)
        processed_docs.append(doc_p)

    np.savez_compressed('data/processed/docs_cleaned', files=processed_docs)    
    logger.info('Process completed')
