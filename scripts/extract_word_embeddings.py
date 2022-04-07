"""Extract word embeddings from documents."""
import logging

from tqdm import tqdm
from typing import List

import gensim
import pickle
from sklearn.feature_extraction.text import CountVectorizer


def extract_embeddings_fom_documents(words: List[str], model: gensim.models.Word2Vec) -> List[str]:
    """Extract unique word embeddings from document collection."""
    emb_words = []
    out_words = []
    for word in words:
        try:
            emb_words.append(model.wv.get_vector(word))
        except KeyError:
            out_words.append(word)
            continue

    logger.info('Number of out-words: %s', len(out_words)) 
    logger.info('Number of embedded-words: %s', len(emb_words))       
    return emb_words


if __name__ == "__main__":
    logger = logging.getLogger("Word-Embeddings-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    
    with open('data/processed/docs_cleaned.pickle', 'rb') as handle:
        processed_docs = pickle.load(handle)

    logger.info('Loading Word2Vec model.')
    model = gensim.models.Word2Vec.load('models/word2vec.model')

    logger.info('Applying Word2Vec model.')
    vectorizer = CountVectorizer()
    vectorizer.fit_transform(processed_docs)

    embedded_words = extract_embeddings_fom_documents(words=vectorizer.get_feature_names(), model=model)

    logger.info('Saving')
    with open("data/processed/words_embedded.pickle", "wb") as fp: 
        pickle.dump(embedded_words, fp,  protocol=pickle.HIGHEST_PROTOCOL)