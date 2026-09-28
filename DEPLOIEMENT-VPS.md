# Mettre HotelManagment en ligne sur un VPS (Systalink, OVH, Hostinger...)

Tout tourne dans Docker : l'application, la base PostgreSQL et le HTTPS automatique.
**L'hébergement mutualisé ne convient pas** (il ne fait tourner que PHP) : prenez un **VPS Ubuntu, 2 Go de mémoire minimum**.

## 1. Le nom de domaine

Chez votre hébergeur de domaine, créez un enregistrement **A** qui pointe vers l'adresse IP du VPS :

```
hotel.mondomaine.ci   A   102.xx.xx.xx
```

Attendez que le domaine réponde (quelques minutes à quelques heures) avant l'étape 4 : sans cela, le certificat HTTPS ne peut pas être délivré.

## 2. Préparer le serveur (une seule fois)

Connectez-vous en SSH, puis :

```
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && exit
```

Reconnectez-vous, puis ouvrez le pare-feu :

```
sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw enable
```

## 3. Installer l'application

```
sudo mkdir -p /opt/hotelmanagment && sudo chown $USER /opt/hotelmanagment
git clone https://gitlab.com/mes_projet/gestion-hotel.git /opt/hotelmanagment
cd /opt/hotelmanagment
cp .env.example .env
nano .env
```

Dans `.env`, remplissez `DOMAINE`, `EMAIL_ADMIN`, `POSTGRES_PASSWORD` et `DJANGO_SECRET_KEY`.
Pour créer la clé secrète :

```
docker run --rm python:3.12-slim python -c "import secrets; print(secrets.token_urlsafe(60))"
```

## 4. Démarrer

```
docker compose up -d --build
docker compose logs -f
```

Le premier démarrage prend plusieurs minutes (construction de l'image). L'application crée les tables toute seule, puis Caddy obtient le certificat HTTPS.

Créez votre compte administrateur :

```
docker compose exec web python manage.py createsuperuser
```

Le site est en ligne : `https://hotel.mondomaine.ci/login/`

## 5. Reprendre vos données actuelles (facultatif)

Sur votre PC :

```
.venv\Scripts\python.exe -X utf8 manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e admin.logentry -e sessions --indent 2 -o donnees.json
scp donnees.json utilisateur@IP_DU_VPS:/opt/hotelmanagment/
```

Sur le serveur :

```
docker compose cp donnees.json web:/app/donnees.json
docker compose exec web python manage.py loaddata /app/donnees.json
rm donnees.json
```

Copiez aussi vos logos : `scp -r media utilisateur@IP_DU_VPS:/tmp/` puis
`docker compose cp /tmp/media/. web:/app/media/`

## 6. Au quotidien

| Action | Commande (dans `/opt/hotelmanagment`) |
|---|---|
| Mettre à jour l'application | `git pull && docker compose up -d --build` |
| Voir les journaux | `docker compose logs -f web` |
| Redémarrer | `docker compose restart web` |
| Arrêter | `docker compose down` (les données sont conservées) |
| Sauvegarder | `./deploy/sauvegarde.sh` |

**Sauvegarde automatique chaque nuit** (`crontab -e`) :

```
0 2 * * * cd /opt/hotelmanagment && ./deploy/sauvegarde.sh >> /var/log/hotel-sauvegarde.log 2>&1
```

Les sauvegardes sont conservées 30 jours dans `/var/sauvegardes/hotelmanagment`. Copiez-les aussi ailleurs (autre serveur ou disque) : une sauvegarde qui reste sur la même machine ne protège pas d'une panne du VPS.

## Sécurité

- Ne publiez jamais le fichier `.env` : il contient la clé secrète et le mot de passe de la base.
- La base PostgreSQL n'est pas accessible depuis Internet : elle ne parle qu'à l'application.
- Seuls les ports 22, 80 et 443 sont ouverts.
- Mettez le serveur à jour de temps en temps : `sudo apt update && sudo apt upgrade -y`.
