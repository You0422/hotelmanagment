# Mise en ligne de HotelManagment (Render + PostgreSQL)

La landing page reste sur **Netlify**. L'application Django va sur **Render** avec une base **PostgreSQL**.
En local, rien ne change : sans `DATABASE_URL`, l'application utilise `db.sqlite3`.

## 1. Mettre le projet sur GitHub

`db.sqlite3`, `.env`, `media/` et `staticfiles/` sont exclus par `.gitignore` (ils ne sont jamais publiés).

## 2. Créer l'application et la base sur Render

1. render.com → **New → Blueprint** → choisir le dépôt GitHub.
2. Render lit `render.yaml` et crée :
   - la base PostgreSQL `hotelmanagment-db` ;
   - le service web `hotelmanagment` (construction : `build.sh`, lancement : `gunicorn`).
3. Les variables sont réglées automatiquement : `DATABASE_URL`, `DJANGO_SECRET_KEY` (générée), `DJANGO_DEBUG=False`.
   L'adresse `https://hotelmanagment.onrender.com` est autorisée automatiquement.

À chaque déploiement, `build.sh` installe les dépendances, prépare le CSS/JS et crée ou met à jour les tables.

## 3. Copier les données existantes (SQLite → PostgreSQL), une seule fois

Depuis le PC, dans le dossier du projet, avec l'environnement virtuel.

Exporter la base locale :

```
.venv\Scripts\python.exe -X utf8 manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e admin.logentry -e sessions --indent 2 -o donnees.json
```

Dans Render, ouvrir la base → **Connect → External Database URL**, copier l'adresse, puis dans PowerShell :

```
$env:DATABASE_URL = "postgresql://...adresse copiée..."
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe -X utf8 manage.py loaddata donnees.json
Remove-Item Env:DATABASE_URL
```

`donnees.json` contient les comptes (mots de passe chiffrés) et les clients : le supprimer après l'import, ne pas le publier.

## 4. Points à connaître (offre gratuite de Render)

- Le service se met en veille après 15 minutes sans visite : environ 30 secondes d'attente à la visite suivante.
- Les fichiers envoyés (logos, justificatifs de dépenses) sont effacés à chaque redéploiement. Il faut un disque persistant (offre payante) ou les renvoyer.
- La base PostgreSQL gratuite expire au bout de 30 jours : passer à une offre payante pour la garder.

## Postgres local (facultatif)

Avec PostgreSQL installé sur le PC, voir `.env.example`, par exemple :
`DATABASE_URL=postgresql://postgres:motdepasse@localhost:5432/hotelmanagment` et `DB_SSL_REQUIRE=False`.
