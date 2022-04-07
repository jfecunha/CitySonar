"""Keyword Extraction using YAKE."""
import logging

from tqdm import tqdm

import numpy as np
import pickle
import yake



if __name__ == "__main__":
    logger = logging.getLogger("Keyword-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    #processed_docs = np.load('data/processed/docs_cleaned.npz', allow_pickle=True)['files']
    with open('data/processed/docs_cleaned.pickle', 'rb') as handle:
        processed_docs = pickle.load(handle)

    language = "pt"
    max_ngram_size = 3
    deduplication_thresold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 10

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
    docs_keywords = []
    for doc in tqdm(processed_docs):
        docs_keywords.append(custom_kw_extractor.extract_keywords(doc))

    logger.info('Saving')
    #np.savez_compressed('data/processed/docs_keywords', files=docs_keywords)
    with open("data/processed/docs_keywords.pickle", "wb") as fp: 
        pickle.dump(docs_keywords, fp,  protocol=pickle.HIGHEST_PROTOCOL)