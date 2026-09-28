# Image de base Python
FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.32 \
    GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    build-essential \
    libpq-dev \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libgeos-dev \
    libproj-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libgobject-2.0-0 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
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
RUN mkdir -p logs media static

# Exposition du port Django
EXPOSE 8080

# Commande par défaut (dev uniquement)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8080"]