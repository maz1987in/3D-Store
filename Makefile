PY=python
BACKEND=backend
VENV?=.venv
PIP=$(VENV)/bin/pip
PYBIN=$(VENV)/bin/python

venv:
	python3 -m venv $(VENV)
	$(PIP) install -q -r $(BACKEND)/requirements.txt

run-api:
	FLASK_APP=backend/app/__init__.py FLASK_RUN_PORT=5000 $(PYBIN) -m flask run --debug

migrate:
	alembic -c backend/alembic.ini upgrade head

seed:
	$(PYBIN) backend/scripts/seed_authz.py

test:
	$(PYBIN) -m pytest backend/tests -q

.PHONY: venv run-api migrate seed test
