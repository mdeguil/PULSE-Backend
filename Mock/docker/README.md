# Déployer la Mock API avec Docker

Depuis ce dossier, construire et démarrer le service :

```bash
docker compose up --build -d
```

Le service écoute sur le port `5000` du conteneur. Le port publié sur l'hôte
est `5000` par défaut et peut être changé avec `API_PORT` (par exemple
`API_PORT=8080 docker compose up --build -d`).

La configuration Supabase est chargée depuis `Mock/.env`, qui doit définir
`SUPABASE_URL` et `SUPABASE_SECRET_KEY` (ou `SUPABASE_SERVICE_ROLE_KEY`).
Ne placez pas ces secrets dans l'image ou dans le fichier Compose. Le fichier
`.env` est exclu du contexte de build.

Les routes d'authentification sont accessibles sous `/api/v1/auth`. Aucun
schéma Supabase n'est créé ou modifié par le service.

Pour consulter les logs et arrêter le service :

```bash
docker compose logs -f mock-auth-api
docker compose down
```
