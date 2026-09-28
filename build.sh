#!/usr/bin/env bash
# Construction sur Render : dépendances, fichiers statiques, tables PostgreSQL
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
