# Mock API d'authentification PULSE

Mock du contrat d'authentification HAC-API-001 v1.2, connecté au projet
Supabase configuré dans `Mock/.env`.

## Tables utilisées

La mock API utilise uniquement la table d'authentification suivante :

| Table Supabase | État | Colonnes utilisées |
|---|---|---|
| `public.utilisateur` | Déjà existante | `user_id`, `email`, `password_hash`, `display_name`, `role`, `account_status` |

`db.py` adapte les colonnes françaises/en `snake_case` au format JSON attendu
par le contrat de l'API (`userId`, `displayName`, `accountStatus`, etc.).
Le jeton de démonstration a la forme `demo-token-<userId>` et est résolu en
recherchant directement l'utilisateur dans `utilisateur`. Il n'est pas stocké
en base.
Les tables métier `preference`, `objectif`, `defi`, `participation`,
`progression` et `contenu` ne sont pas utilisées par cette mock API; elles ne
sont donc pas recréées ici.

La mock API ne crée, ne modifie ni ne supprime aucune table ou colonne
Supabase.

Les utilisateurs doivent avoir un mot de passe haché au format PBKDF2
`pbkdf2_sha256$...` attendu par `security.py`. L'email est recherché en
minuscules. Les rôles et statuts doivent correspondre à ceux attendus par
l'API, notamment `USER` / `FUNCTIONAL_ADMIN` et `ACTIVE` / `DISABLED`.

## Configuration et démarrage

Dans `Mock/.env`, configurer `SUPABASE_URL` et `SUPABASE_SECRET_KEY` avec les
valeurs du même projet. Garder la clé serveur secrète; ne pas utiliser la clé
publishable/anon côté API. `SUPABASE_SERVICE_ROLE_KEY` est accepté comme nom
alternatif.

```bash
python -m pip install -r requirements.txt
python app.py
pytest -v
```

Le client Supabase est créé au démarrage. Les erreurs d'accès aux tables ou de
connexion sont journalisées côté serveur et retournent un `503` au client.
Les tests utilisent un faux client mémoire et ne modifient pas le projet
Supabase.

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Vérifie email et mot de passe, retourne un jeton Bearer |
| GET | `/api/v1/auth/me` | Retourne l'identité associée au jeton |

Routes de recette : `SIMULATE_UNAVAILABLE=true`, `POST /simulator/unavailable`
avec `{"enabled": true|false}`, ou l'en-tête
`X-Simulate-Unavailable: true`.
