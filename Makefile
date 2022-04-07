export PYTHONPATH := .:$(PYTHONPATH)

data-etl:
	poetry run python scripts/data_prep.py

train-word2vec:
	poetry run python scripts/embeddings.py

extract-yake-keywords:
	poetry run python scripts/keywords.py

extract-word-embeddings:
	poetry run python scripts/extract_word_embeddings.py
