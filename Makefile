.PHONY: install install-dev run test smoke train serve-web

PYTHON ?= python
STREAMLIT ?= streamlit
PORT ?= 8000

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(STREAMLIT) run app1.py

test:
	pytest -q

smoke:
	$(PYTHON) scripts/smoke_test.py

train:
	$(PYTHON) scripts/train_risk_model.py \
		--dataset data/construction_dataset.csv \
		--model-out models/risk_classifier.joblib \
		--metrics-out models/risk_model_metrics.json \
		--model-version v1-advisory-multimodel

serve-web:
	$(PYTHON) -m http.server $(PORT)
