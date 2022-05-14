export PYTHONPATH := .:$(PYTHONPATH)

arquivo-scraper:
	poetry run python scripts/arquivo_scraper.py

publico-scraper:
	poetry run python scripts/publico_scraper.py

data-cleaning:
	poetry run python scripts/data_prep.py

train-category-classifier:
	poetry run python scripts/category_classifier.py

extract-categories:
	poetry run python scripts/extract_categories.py

extract-keywords-publico:
	poetry run python scripts/extract_publico_keywords.py

run-app:
	poetry run python streamlit run app/streamlit_app.py

train-word2vec:
	poetry run python scripts/embeddings.py

extract-yake-keywords:
	poetry run python scripts/extract_keywords.py

extract-word-embeddings:
	poetry run python scripts/extract_word_embeddings.py \
	--pre_trained 0 \
	--out_file words_embedded

train-concept-model:
	poetry run python scripts/clustering.py

train-sentiment-classifier:
	poetry run python scripts/sentiment_classifier.py

extract-keyword-sentiment:
	poetry run python scripts/extract_keywords_sentiment.py

