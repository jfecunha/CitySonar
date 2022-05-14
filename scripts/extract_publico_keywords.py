"""Extract Publico articles keywords."""
import logging

from tqdm import tqdm

import pandas as pd
import yake


if __name__ == "__main__":
    logger = logging.getLogger("Data-Prep")
    logging.basicConfig(level=logging.INFO)
    
    logger.info('Loading data')
    publico_articles = pd.read_csv('data/processed/publico_docs_cleaned.csv.gz', compression='gzip')

    language = "pt"
    max_ngram_size = 2
    deduplication_thresold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 5

    custom_kw_extractor = yake.KeywordExtractor(
        lan=language, 
        n=max_ngram_size, 
        dedupLim=deduplication_thresold, 
        dedupFunc=deduplication_algo, 
        windowsSize=windowSize, 
        top=numOfKeywords, 
        features=None
    )

    logger.info('Extracting keywords')
    publico_articles['keywords'] = publico_articles['body'].apply(lambda val: custom_kw_extractor.extract_keywords(val))
    publico_articles['keywords'] = publico_articles['keywords'].apply(lambda val: [v[0] for v in val])
    logger.info('Saving')
    publico_articles.to_csv('data/processed/publico_docs_cleaned_w_keywords.csv.gz', compression='gzip', index=False)
