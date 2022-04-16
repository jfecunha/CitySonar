"""Sentiment classifier."""
import logging

from typing import List

import pandas as pd
import numpy as np
import pickle
import fasttext

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report
from sklearn import linear_model



def sentiment(val):
    if val < 3:
        return 'Negative'
    elif val == 3:
        return 'Neutral'
    elif val > 3:
        return 'Positive'


if __name__ == "__main__":
    
    logger = logging.getLogger("Word-Embeddings-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    df = pd.read_csv('data/external_corpus/concatenated.csv')

    features = ['sentiment', 'review_text_processed']

    df['sentiment'] = df['rating'].apply(lambda val : sentiment(val))

    df = df[features].iloc[0:]

    df.dropna(inplace=True)

    print(df.sentiment.value_counts())

    X = df['review_text_processed']
    Y = df['sentiment']

    logger.info('Creating partitions.')
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
    for train_index, test_index in sss.split(X, Y ):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = Y.iloc[train_index], Y.iloc[test_index]

    # logger.info('Extracting features.')
    # vectorizer = TfidfVectorizer()
    # X_train_ = vectorizer.fit_transform(X_train)
    # X_test_= vectorizer.transform(X_test)

    df_train = pd.DataFrame() 
    df_train['sentiment'] = y_train
    df_train['review'] = X_train
    df_train['sentiment'] = df_train['sentiment'].apply(lambda val: f'__label__{val}')

    np.savetxt('data/processed/train-set.txt', df_train.values, fmt = "%s")

    print(df_train.shape)

    df_test = pd.DataFrame() 
    df_test['sentiment'] = y_test
    df_test['review'] = X_test
    df_test['sentiment'] = df_test['sentiment'].apply(lambda val: f'__label__{val}')

    print(df_test.shape)

    logger.info('Training.')
    model = fasttext.train_supervised(input="data/processed/train-set.txt", lr=0.05, epoch=100, wordNgrams=3)
    
    logger.info('Evaluating.')
    df_test['Pred'] = df_test['review'].apply(lambda val: model.predict(val.replace('\n', ''))[0][0])
    
    print(classification_report(df_test['sentiment'], df_test['Pred']))

    model.save_model("models/trained/fasttext-sentiment.bin")

    print(model.get_nearest_neighbors('desporto'))
    print(model.predict("este restaurante e fraco!"))

    # svc = linear_model.SGDClassifier(loss='hinge', class_weight='balanced')
    # svc.fit(X_train_, y_train)

