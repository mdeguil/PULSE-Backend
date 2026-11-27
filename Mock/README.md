# API PULSE — démarrage et configuration

Ce dossier contient la Mock API d'authentification HAC-API-001 v1.2. Elle
consulte Supabase. Le backend Java PULSE est un service séparé et relaie les
appels d'authentification vers cette API.

## Démarrer la Mock API avec Docker

Créer `Mock/.env` avec les identifiants du projet Supabase :

```dotenv
SUPABASE_URL=https://<projet>.supabase.co
SUPABASE_SECRET_KEY=<cle-secrete-serveur>
```

`SUPABASE_SERVICE_ROLE_KEY` est accepté comme nom alternatif. Ne jamais
utiliser la clé publishable/anon pour l'API serveur, ni committer ce fichier.

Depuis la racine du dépôt, construire et démarrer uniquement la Mock API :

```powershell
docker compose -f Mock/docker/docker-compose.yml up --build -d
```

Pour consulter les logs et arrêter les services :

```powershell
docker compose -f Mock/docker/docker-compose.yml logs -f
docker compose -f Mock/docker/docker-compose.yml down
```

La Mock API est accessible depuis l'hôte sur `http://localhost:5000`.
Le port hôte peut être changé avec `API_PORT` :

```powershell
$env:API_PORT = "5001"
docker compose -f Mock/docker/docker-compose.yml up --build -d
```

## Routes d'authentification

Les routes exposées par la Mock API sont :

| Méthode | Route | Résultat |
|---|---|---|
| POST | `/api/v1/auth/login` | Vérifie `email` et `password`; retourne un jeton Bearer |
| GET | `/api/v1/auth/me` | Retourne l'identité correspondant au jeton Bearer |

Le backend PULSE relaie ces routes et leurs réponses quand il est démarré
séparément. Depuis un processus Java lancé sur l'hôte, l'adresse par défaut
de l'API amont est `http://localhost:5000`. Depuis un conteneur séparé, la
configuration doit utiliser une adresse joignable depuis ce conteneur; son
`localhost` ne pointe pas vers la Mock API.

## Supabase et schéma existant

La Mock API utilise uniquement la table existante `public.utilisateur` et les
colonnes `user_id`, `email`, `password_hash`, `display_name`, `role` et
`account_status`. Elle ne crée ni ne modifie aucune table ou colonne.
Les utilisateurs doivent avoir un mot de passe PBKDF2 au format
`pbkdf2_sha256$...`; les rôles/statuts attendus sont `USER` ou
`FUNCTIONAL_ADMIN`, et `ACTIVE` ou `DISABLED`.

Les jetons démo sont de la forme `demo-token-<userId>` et ne sont pas stockés
en base. Le backend Java ne reçoit pas les secrets Supabase.

## Développement sans Docker

La Mock API peut être lancée seule depuis `Mock` avec :

```powershell
python -m pip install -r requirements.txt
python app.py
python -m pytest -q
```

Le backend Java peut être lancé séparément depuis `pulse`. Sa propriété
`PULSE_AUTH_API_BASE_URL` doit pointer vers la Mock API (par défaut
`http://localhost:5000`) :

```powershell
.\mvnw.cmd spring-boot:run
```

## Simulation des erreurs d'authentification

La Mock API expose les routes de contrat `POST /api/v1/auth/login` et
`GET /api/v1/auth/me`, avec les réponses `400`, `401`, `403` et `503`.
Pour simuler une indisponibilité, définir `SIMULATE_UNAVAILABLE=true`, appeler
`POST /simulator/unavailable` avec `{"enabled": true|false}`, ou envoyer
`X-Simulate-Unavailable: true`.
