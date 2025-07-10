#!/bin/bash

echo "[INFO] Installing main dependencies"
export PYTHONPATH="$(pwd)"
poetry install
pre-commit install --install-hooks

echo
echo "[INFO] Performing migrations"
poetry run python3 manage.py migrate

echo
echo "[INFO] Run tests"
poetry run python3 manage.py test tests
