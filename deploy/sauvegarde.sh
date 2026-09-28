#!/usr/bin/env bash
# Sauvegarde de la base et des fichiers envoyés (logos, justificatifs).
# Utilisation : ./deploy/sauvegarde.sh [dossier_de_destination]
# Chaque nuit à 2h : 0 2 * * * cd /opt/hotelmanagment && ./deploy/sauvegarde.sh >> /var/log/hotel-sauvegarde.log 2>&1
set -o errexit

DEST="${1:-/var/sauvegardes/hotelmanagment}"
JOUR="$(date +%Y-%m-%d_%Hh%M)"
GARDER_JOURS=30

mkdir -p "$DEST"
set -a; . ./.env; set +a

echo "[$JOUR] Sauvegarde de la base..."
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$DEST/base_$JOUR.sql.gz"

echo "[$JOUR] Sauvegarde des fichiers envoyés..."
docker compose run --rm -T -v "$DEST:/sauvegardes" web tar czf "/sauvegardes/media_$JOUR.tar.gz" -C /app media

find "$DEST" -name '*.gz' -mtime +$GARDER_JOURS -delete
echo "[$JOUR] Terminé : $DEST"
