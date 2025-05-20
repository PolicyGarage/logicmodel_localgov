.PHONY: run lint format check

run:
	PYTHONPATH=. streamlit run src/app.py

lint:
	ruff check .
	pyright .

format:
	ruff format .

check:
	ruff check . && ruff format --check .
