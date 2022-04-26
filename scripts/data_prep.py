import logging

import pandas as pd
import spacy

from nlpiper.core import Document
from nlpiper.core import Compose
from nlpiper.transformers import cleaners
from joblib import Parallel, delayed 

from src.cleaners import TextCleaner
from resources.stopwords import WORDS

def process_stop_words():
    """Prepare stop words."""
    pipeline = Compose([
            cleaners.CleanURL(),
            cleaners.CleanEOF(),
            cleaners.CleanMarkup(),
            cleaners.CleanAccents(),
            cleaners.CleanNumber()
    ])
    stop_words = Document(WORDS)
    stop_words = pipeline(stop_words)
    stop_words = stop_words.cleaned.split(' ')
    stop_words = list(filter(None, stop_words))
    return stop_words

def apply_cleaning(document: str, transformer: TextCleaner) -> str:
    """Applying cleaning on dataframe."""
    doc_p = transformer(document)
    return doc_p


if __name__ == "__main__":
    logger = logging.getLogger("Data-Prep")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    data = pd.read_csv('data/scraping_data_v2.csv.gz', compression='gzip')
    
    logger.info('Number of records before filters: %s', len(data))
    
    logger.info('Remove Nan')
    data.dropna(inplace=True)
    
    data = data[(data['year']>=2014)]
    
    data['link_len'] = data.link.apply(lambda val: len(val))
    mode_link_value = data['link_len'].mode().item()
    data = data[data['link_len'] >= mode_link_value] # links above the mode contain multiple articles within same page
    
    # Guarantee that the city is in the article body
    data['check'] = data.apply(lambda val: val['city'].lower() in val['content'].lower(), axis=1)
    data = data[data['check']==True]

    # Discard noise articles from jn.pt
    data = data[~data['title'].str.contains('DESCONTO')]
    logger.info('Number of records after filters: %s', len(data))

    model= spacy.load("pt_core_news_lg")
    tc = TextCleaner(model=model, stop_words=process_stop_words())

    logger.info('Applying cleaning')
    processed_docs_content = Parallel(n_jobs=1)(delayed(apply_cleaning)(doc, tc) for doc in data['content'].to_list())
    processed_docs_title = Parallel(n_jobs=1)(delayed(apply_cleaning)(doc, tc) for doc in data['title'].to_list())
 
    logger.info('Saving')
    data['content_p'] = processed_docs_content
    data['title_p'] = processed_docs_title

    data.to_csv('data/processed/docs_cleaned.csv.gz', compression='gzip', index=False)   
    logger.info('Process completed')
