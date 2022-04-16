"""Extract concepts from documents."""
import logging

from tqdm import tqdm

import pickle

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score



if __name__ == "__main__":
    logger = logging.getLogger("Concept-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    with open('data/processed/words_embedded.pickle', 'rb') as handle:
        words_emb = pickle.load(handle)
    
    logger.info('Preprocesing Embeddings')
    data = [val[0] for val in words_emb]

    logger.info('Applying Grid Search to find best k')
    ks = range(2, 20)
    results = {}
    for k in tqdm(ks):
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(data)
        results[k] = silhouette_score(data, kmeans.labels_)
        print(results)

    logger.info('Training with best k')
    best_k = max(results, key=results.get)
    print('Selected k:', best_k)
    kmeans = KMeans(n_clusters=best_k, random_state=0)
    kmeans.fit(data)

    logger.info('Saving model')
    with open("models/trained/concepts-model.pickle", "wb") as fp: 
        pickle.dump(kmeans, fp,  protocol=pickle.HIGHEST_PROTOCOL)
