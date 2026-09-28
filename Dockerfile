# Image de base Python
FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Dépendances système : PostgreSQL et les bibliothèques nécessaires aux PDF
# (reportlab, svglib et pycairo pour les factures, reçus et fiches client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    postgresql-client \
    libcairo2-dev \
    libffi-dev \
    pkg-config \
    python3-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copier uniquement requirements (optimisation cache Docker)
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs media staticfiles

# Port de l'application
EXPOSE 8080

# Démarrage : tables à jour, fichiers CSS/JS préparés, puis serveur gunicorn
# PORT est fourni par l'hébergeur (Railway, Render...), 8080 par défaut
CMD ["sh", "-c", "python manage.py migrate --no-input && python manage.py collectstatic --no-input && gunicorn prohotel.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers ${WEB_CONCURRENCY:-3} --timeout 120 --access-logfile -"]
