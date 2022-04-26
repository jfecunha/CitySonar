"""Extract categories from scraped data."""
import logging

import fasttext
import pandas as pd

if __name__ == "__main__":
    
    logger = logging.getLogger("Category-Extraction")
    logging.basicConfig(level=logging.INFO)

    logger.info('Loading data and model')
    scraped_data_p = pd.read_csv('data/processed/docs_cleaned.csv.gz', compression='gzip')
    model = fasttext.load_model('models/trained/category-classifier.bin')

    logger.info('Applying model')
    scraped_data_p['category'] = scraped_data_p['content_p'].apply(
        lambda val: model.predict(''.join(val))[0][0].replace('__label__', '')
    )

    logger.info('Saving')
    scraped_data_p.to_csv('data/processed/docs_cleaned_w_categories.csv.gz', compression='gzip', index=False)   

    logger.info('Check')
    print(scraped_data_p['category'].value_counts())
