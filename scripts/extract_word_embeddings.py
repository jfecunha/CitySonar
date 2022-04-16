"""Extract word embeddings from documents."""
import argparse
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
            emb_words.append((model.wv.get_vector(word) if args.pre_trained != 1 else model.get_word_vector(word), word))
        except KeyError:
            out_words.append(word)
            continue

    logger.info('Number of out-words: %s', len(out_words)) 
    logger.info('Number of embedded-words: %s', len(emb_words))       
    return emb_words


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pre_trained', type=int, help='1 for pre-trained and 0 for custom model.')
    parser.add_argument('--out_file', type=str, help='filename for output.')
    args = parser.parse_args()

    logger = logging.getLogger("Word-Embeddings-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    
    with open('data/processed/docs_cleaned.pickle', 'rb') as handle:
        processed_docs = pickle.load(handle)

    logger.info('Loading Word2Vec model.')
    if args.pre_trained == 1:
        #from gensim.models import KeyedVectors
        logging.info('Using pre-trained model')
        #model = KeyedVectors.load_word2vec_format('models/pre-trained/cbow_s100.txt')
        import fasttext
        model = fasttext.load_model('models/trained/fasttext-sentiment.bin')

    else:
        model = gensim.models.Word2Vec.load('models/trained/word2vec.model')

    logger.info('Applying Word2Vec model.')
    vectorizer = CountVectorizer()
    vectorizer.fit_transform(processed_docs)

    embedded_words = extract_embeddings_fom_documents(words=vectorizer.get_feature_names(), model=model)

    logger.info('Saving')
    with open(f"data/processed/{args.out_file}.pickle", "wb") as fp: 
        pickle.dump(embedded_words, fp,  protocol=pickle.HIGHEST_PROTOCOL)