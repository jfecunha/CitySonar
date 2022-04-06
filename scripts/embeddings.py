"""Train Word2Vec model."""
import logging

import numpy as np

from gensim.models import Word2Vec

if __name__ == "__main__":
    logger = logging.getLogger("Word2vec-train")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    processed_docs = np.load('data/processed/docs_cleaned.npz', allow_pickle=True)['files']

    logger.info('Prepare corpus')
    processed_docs = [doc.split(' ') for doc in processed_docs]

    logger.info('Init training')
    model = Word2Vec(sentences=processed_docs, vector_size=100, window=5, min_count=1, workers=4, sg=0, epochs=30)

    logger.info('Quality check')
    print(model.wv.most_similar('rei', topn=10))

    model.save("models/word2vec.model")
