export PYTHONPATH := .:$(PYTHONPATH)

arquivo-scraper:
	poetry run python scripts/arquivo_scraper.py

publico-scraper:
	poetry run python scripts/publico_scraper.py

data-cleaning:
	poetry run python scripts/data_prep.py

train-category-classifier:
	poetry run python scripts/category_classifier.py

extract-arquivo-categories:
	poetry run python scripts/extract_categories.py

extract-keywords-publico:
	poetry run python scripts/extract_publico_keywords.py

run-app:
	poetry run python streamlit run app/streamlit_app.py
