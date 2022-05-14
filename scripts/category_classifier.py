"""Category classifier."""

import logging

from tqdm import tqdm

import pandas as pd
import numpy as np
import fasttext
import spacy

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, f1_score

from scripts.data_prep import process_stop_words, apply_cleaning
from src.cleaners import TextCleaner


tags = ['sociedade', 'local', 'fugas', 'politica', 'desporto', 'p3', 'culturaipsilon', 'economia', 'ciencia', 'tecnologia', 'ecosfera']

tags_to_split = ['sociedade', 'local', 'p3']

tags_rename = {
    'fugas': 'Turismo/Lazer', 
    'desporto': 'Desporto',
    'politica': 'Politica',
    'economia': 'Economia',
    'ciencia': 'Ciencia',
    'culturaipsilon': 'Cultura',
    'tecnologia' : 'Tecnologia',
    'ecosfera': 'Ambiente',
}

sub_tags = {
    'Saude': ['SAÚDE', 'CORONAVÍRUS', 'COVID-19', 'HOSPITAIS', 'SERVIÇO NACIONAL DE SAÚDE', 'NATALIDADE', 'ASAE', 'INEM'],
    'Ambiente': ['METEOROLOGIA', 'MAU TEMPO', 'CLIMA', 'IPMA', 'AMBIENTE', 'ÁGUA', 'SUSTENTABILIDADE', 'FLORESTAS'],
    'Incendios': ['INCÊNDIOS', 'INCÊNDIO','INCÊNDIOS FLORESTAIS'],
    'Forças-Segurança': ['GNR', 'POLÍCIA JUDICIÁRIA', 'PROTECÇÃO CIVIL', 'PSP', 'SERVIÇO DE ESTRANGEIROS E FRONTEIRAS', 'BOMBEIROS'],
    'Educacao': ['ENSINO SUPERIOR', 'EDUCAÇÃO'],
    'Justica' : ['JUSTIÇA', 'MINISTÉRIO PÚBLICO'],
    'Religiao': ['IGREJA CATÓLICA', 'RELIGIÃO'],
    'Crime': ['CRIME', 'VIOLÊNCIA DOMÉSTICA', 'PRISÕES', 'TRÁFICO DE SERES HUMANOS', 'TRÁFICO DE DROGA'],
    'Acidentes' : ['ACIDENTES', 'SEGURANÇA RODOVIÁRIA', 'ESTRADAS'],
    'Transportes' : ['TRANSPORTES', 'COMBOIOS', 'MOBILIDADE', 'BICICLETAS', 'CP', 'MOBILIDADE', 'AVIAÇÃO'],
    'Local' : [
        'LISBOA', 'COIMBRA', 'AVEIRO', 'SETÚBAL', 'VIANA DO CASTELO', 'PORTO', 'BRAGANÇA', 'BRAGA', 'BEJA', 'VISEU', 'ÉVORA',
        'CÂMARA DE VISEU', 'CÂMARA DE LISBOA', 'VILA REAL', 'ALGARVE', 'LEIRIA', 'CASTELO BRANCO', 'FARO', 'SANTARÉM', 'ALENTEJO',
        'CÂMARA DO PORTO', 'PORTALEGRE', 'CÂMARA DE COIMBRA', 'CÂMARA DE BRAGA', 'GUARDA', 'AUTARQUIAS'
    ],
    'Habitacao' : ['HABITAÇÃO', 'PATRIMÓNIO'],
    'Cultura': ['ARTES', 'MÚSICA', 'CULTURA', 'FESTIVAL', 'EVENTO', 'ARTE URBANA', 'STREET ART', 'TEATRO', 'MUSEUS'],
    'Tecnologia': ['TECNOLOGIA'],
    'Turismo/Lazer': ['TURISMO'],
    'Sociedade': ['CRIANÇAS', 'SOLIDARIEDADE', 'CIGANOS', 'SEGURANÇA SOCIAL', 'IDOSOS', 'ANIMAIS']
}

def assign_category(val, sub_tags):
    for key, values in sub_tags.items():
        if val in values:
            return(key)
    return 'Outros'


if __name__ == "__main__":
    logger = logging.getLogger("Data-Prep")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data')
    data_source = pd.read_csv('data/raw/publico_scraper.csv.gz', compression='gzip')
    data_source.dropna(inplace=True)
    data_source.drop_duplicates(inplace=True)

    logger.info('Preprocessing')
    data = data_source[data_source['main_tag'].isin(tags)]

    data_to_split = data[data['main_tag'].isin(tags_to_split)]
    data_not_to_split = data[~data['main_tag'].isin(tags_to_split)]

    # Build target 
    data_to_split['category'] = data_to_split['tag'].apply(lambda val: assign_category(val, sub_tags))
    data_not_to_split['category'] = data_not_to_split['main_tag'].apply(lambda val: tags_rename[val])
    data_source_p = pd.concat([data_not_to_split, data_to_split], ignore_index=True)

    data_source_p = data_source_p[~data_source_p['category'].isin(['Opiniao', 'Outros', 'Local'])]
    print(data_source_p.shape)
    print(data_source_p.category.value_counts())

    logger.info('Applying cleaning')
    model = spacy.load("pt_core_news_lg")
    tc = TextCleaner(model=model, stop_words=process_stop_words())

    data_source_p['body_p'] = [apply_cleaning(doc, tc) for doc in tqdm(data_source_p['body'].to_list())]
    data_source_p.to_csv('data/processed/publico_docs_cleaned.csv.gz', index=False)
    
    X = np.array(data_source_p['body_p'].to_list())
    Y = np.array(data_source_p['category'].tolist())

    logger.info('Applying cross-validation')
    score = []
    sss = StratifiedShuffleSplit(n_splits=2, test_size=0.2, random_state=0)
    for train_index, test_index in sss.split(X, Y ):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = Y[train_index], Y[test_index]
        
        df_train = pd.DataFrame() 
        df_train['category'] = y_train
        df_train['body'] = X_train
        df_train['category'] = df_train['category'].apply(lambda val: f'__label__{val}')

        np.savetxt('categories-train.txt', df_train.values, fmt = "%s")

        print(df_train.shape)

        df_test = pd.DataFrame() 
        df_test['category'] = y_test
        df_test['body'] = X_test
        df_test['category'] = df_test['category'].apply(lambda val: f'__label__{val}')

        print(df_test.shape)

        model = fasttext.train_supervised(input="categories-train.txt", lr=1, epoch=100, wordNgrams=5)
        df_test['Pred'] = df_test['body'].apply(lambda val: model.predict(val)[0][0])
        print(classification_report(df_test['category'], df_test['Pred']))
        score.append(f1_score(y_test, df_test['Pred'], average='macro'))

    logger.info('Mean f1-score for folds %s', np.mean(score))
    
    logger.info('Training with entire dataset')
    dataset = pd.DataFrame() 
    dataset['category'] = y_train
    dataset['body'] = X_train
    dataset['category'] = dataset['category'].apply(lambda val: f'__label__{val}')
    np.savetxt('categories-all.txt', dataset.values, fmt = "%s")
    model = fasttext.train_supervised(input="categories-train.txt", lr=1, epoch=200, wordNgrams=5)

    logger.info('Saving model')
    model.save_model("models/trained/category-classifier.bin")


