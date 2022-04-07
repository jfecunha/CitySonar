"""Train Word2Vec model."""
import logging

import numpy as np
import pickle

from gensim.models import Word2Vec

if __name__ == "__main__":
    logger = logging.getLogger("Word2vec-train")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    with open('data/processed/docs_cleaned.pickle', 'rb') as handle:
        processed_docs = pickle.load(handle)

    logger.info('Prepare corpus')
    processed_docs = [doc.split(' ') for doc in processed_docs]

    logger.info('Init training')
    model = Word2Vec(sentences=processed_docs, vector_size=100, window=5, min_count=1, workers=4, sg=0, epochs=30)

    logger.info('Quality check')
    print(model.wv.most_similar('rei', topn=10))

    model.save("models/word2vec.model")
