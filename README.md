# IrrigaSmart — Backend complet

Projet Django autonome : `accounts` (authentification + rôles),
`irrigation` (parcelles, capteurs, irrigation/drainage, temps réel
WebSocket), `administration` (gestion des utilisateurs et vue
d'ensemble des parcelles pour l'admin).

## Installation

```bash
# 1. Environnement virtuel
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

# 2. Dépendances
pip install -r requirements.txt

# 3. Configuration
cp .env.example .env
# ouvre .env et ajuste les valeurs si besoin (les valeurs par défaut
# suffisent pour tester en local sans rien changer)

# 4. Base de données
python manage.py makemigrations accounts irrigation
python manage.py migrate

# 5. Ton compte administrateur
python manage.py create_admin --email admin@irrigasmart.cm --name "Administrateur" --password "MotDePasseSolide"

# 6. Lancer le serveur
python manage.py runserver
```

`channels` prend automatiquement le relais de `runserver` — pas de
commande différente à connaître en local. Le serveur tourne sur
`http://127.0.0.1:8000`, WebSocket compris (`ws://127.0.0.1:8000/ws/...`).

## Fichier .env — ce que tu peux changer sans toucher au code

| Variable | Rôle | Valeur par défaut |
|---|---|---|
| `SECRET_KEY` | clé secrète Django | une valeur de dev, **à changer en prod** |
| `DEBUG` | mode debug | `True` |
| `ALLOWED_HOSTS` | domaines autorisés | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | domaines autorisés à appeler l'API (prod uniquement) | vide (tout est autorisé en dev) |
| `DATABASE_URL` | vide = SQLite, sinon PostgreSQL | vide |
| `TIME_ZONE` | fuseau horaire | `Africa/Douala` |

## Déploiement (ex: Render)

- `DEBUG=False`, `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS` renseignés avec
  le vrai domaine.
- `DATABASE_URL` pointant vers ta base PostgreSQL Render.
- Commande de démarrage :
  ```bash
  daphne -b 0.0.0.0 -p $PORT config.asgi:application
  ```
  (pas `gunicorn` — Channels a besoin d'un serveur ASGI, pas WSGI)

## Structure

```
manage.py
config/
  settings.py     -> lit tout depuis .env
  urls.py
  asgi.py         -> HTTP + WebSocket
  wsgi.py
accounts/         -> User, JWT, rôles (agriculteur/administrateur)
irrigation/       -> parcelles, matériels, mesures, irrigation/drainage, WebSocket
administration/   -> CRUD utilisateurs + vue d'ensemble parcelles (admin)
.env.example      -> à copier en .env
requirements.txt
```

## Capteur IoT (ESP32)

Chaque parcelle a une `device_key` unique (visible dans l'app, écran
détail d'une parcelle). Le capteur l'envoie dans un header, sans JWT :

```
PATCH /irrigation/parcelles/<id>/mesures/temps-reel/
Headers: X-Device-Key: <la clé de cette parcelle>
Body: {"temperature": 26.4}
```

## Endpoints — résumé

Voir les README des zips précédents pour le détail complet ; en bref :
- `accounts` : `/api/auth/register/`, `/login/`, `/token/refresh/`, `/logout/`, `/me/`
- `irrigation` : `/irrigation/parcelles/...` (CRUD, matériels, mesures, irrigation/drainage, historique, prévision)
- `administration` : `/api/admin/users/...`, `/api/admin/parcelles/...`
- WebSocket : `ws://.../ws/parcelles/<id>/?token=<access_token>`
