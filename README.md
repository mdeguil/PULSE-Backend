# PULSE Backend

PULSE est un backend Java Spring Boot qui relaie actuellement l'authentification
vers une API Flask de démonstration. Cette API consulte Supabase. Les deux
services se démarrent séparément : le Compose de ce dépôt lance uniquement
l'API Flask; le backend Java se lance depuis `pulse`.

> **Important — usage de démonstration :** l'API Flask génère des jetons
> déterministes `demo-token-<userId>`. Bien que la réponse annonce
> `expiresIn: 3600`, l'expiration n'est pas appliquée. Ce mécanisme n'est pas
> destiné à sécuriser un service en production.

## Contenu du dépôt

| Dossier | Rôle |
|---|---|
| `Mock/` | API d'authentification Flask, accès à la table Supabase `utilisateur`, tests et configuration Docker |
| `pulse/` | Backend Spring Boot, relais HTTP des routes d'authentification et entités du domaine |
| `docs/` | Documentation fonctionnelle, conventions d'API, règles métier, modèle de données et scénarios d'acceptation |

Le backend PULSE expose actuellement les routes d'authentification décrites
ci-dessous. Les entités du domaine sont présentes, mais les autres routes métier
décrites dans la documentation ne sont pas encore implémentées.

## Prérequis

- **Git**, pour obtenir le dépôt.
- **Docker Desktop** avec Docker Compose v2, pour démarrer la Mock API dans un conteneur.
- **Java JDK 17 ou supérieur**, pour exécuter PULSE. Le Maven Wrapper inclus télécharge Maven si nécessaire.
- **Python 3.12 recommandé**, uniquement pour lancer la Mock API ou ses tests hors Docker.
- Un projet Supabase avec la table `public.utilisateur` déjà créée et renseignée.
- Un accès réseau à Supabase. Le premier lancement peut aussi nécessiter un accès Internet pour télécharger les dépendances.

Vérifier les outils dans PowerShell :

```powershell
git --version
docker --version
docker compose version
java -version
py -3.12 --version
```

Node.js n'est pas nécessaire pour démarrer ces deux services.

## Installation et configuration

Cloner le dépôt, puis se placer à sa racine :

```powershell
git clone https://github.com/mdeguil/PULSE-Backend.git
Set-Location .\PULSE-Backend
```

Créer le fichier **non versionné** `Mock/.env` avec les identifiants du projet
Supabase :

```dotenv
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SECRET_KEY=<server-secret-key>
```

La variable `SUPABASE_SERVICE_ROLE_KEY` est acceptée à la place de
`SUPABASE_SECRET_KEY`. La clé doit être une clé serveur secrète, jamais une clé
publishable/anon. Ne pas partager ni committer le fichier `.env`.

La Mock API lit uniquement les colonnes suivantes de la table existante
`public.utilisateur` :

`user_id`, `email`, `password_hash`, `display_name`, `role`, `account_status`

Elle ne crée ni ne modifie de table ou de colonne. Les mots de passe stockés
doivent être des hachages PBKDF2 au format attendu par l'API; ils ne sont pas
stockés en clair.

## Démarrer l'API d'authentification

Depuis la racine du dépôt, construire et démarrer **uniquement** la Mock API :

```powershell
docker compose -f Mock/docker/docker-compose.yml up --build -d
```

Par défaut, elle est accessible depuis la machine sur
`http://localhost:5000`. Pour consulter ses logs et son état :

```powershell
docker compose -f Mock/docker/docker-compose.yml ps
docker compose -f Mock/docker/docker-compose.yml logs -f mock-auth-api
Invoke-RestMethod http://localhost:5000/simulator/unavailable
```

La dernière commande appelle une route de diagnostic qui doit retourner l'état
de simulation, par exemple `enabled: False`. Elle confirme que le serveur HTTP
répond, mais ne vérifie pas à elle seule l'accès à Supabase.

Pour publier l'API sur un autre port hôte, définir `API_PORT` avant le
démarrage. L'API continuera d'écouter sur le port 5000 à l'intérieur du
conteneur :

```powershell
$env:API_PORT = "5001"
docker compose -f Mock/docker/docker-compose.yml up --build -d
```

Dans cet exemple, son URL depuis la machine devient
`http://localhost:5001`. Pour arrêter le conteneur :

```powershell
docker compose -f Mock/docker/docker-compose.yml down
```

### Lancer la Mock API directement avec Python

Cette option est utile pour le développement sans Docker. Depuis la racine du
dépôt :

```powershell
Set-Location .\Mock
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Le serveur de développement Flask écoute sur `http://localhost:5000`. Le
fichier `Mock/.env` est chargé automatiquement. Pour quitter, utiliser
`Ctrl+C`.

## Démarrer le backend PULSE

Lancer cette étape dans un terminal PowerShell séparé, une fois la Mock API
démarrée. Depuis la racine du dépôt :

```powershell
$env:PULSE_AUTH_API_BASE_URL = "http://localhost:5000"
Set-Location .\pulse
.\mvnw.cmd spring-boot:run
```

`PULSE_AUTH_API_BASE_URL` désigne l'URL de base de l'API Flask, sans ajouter
`/api/v1/auth`. Sa valeur par défaut est `http://localhost:5000`; adaptez-la si
vous avez changé `API_PORT` ou si l'API est déployée ailleurs. Lorsque PULSE
tourne dans un conteneur séparé, `localhost` désigne ce conteneur : configurez
alors une adresse joignable depuis celui-ci, par exemple
`http://host.docker.internal:5000` sous Docker Desktop.

Le backend écoute par défaut sur `http://localhost:8080`. Le client de
l'application doit appeler PULSE, et non l'API Flask directement.

### Vérifier une connexion

Remplacer les valeurs d'exemple par l'adresse et le mot de passe d'un
utilisateur existant dans Supabase :

```powershell
$body = @{
    email = "utilisateur@example.com"
    password = "<mot-de-passe>"
} | ConvertTo-Json

$session = Invoke-RestMethod `
    -Uri "http://localhost:8080/api/v1/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$session
```

La réponse de succès contient notamment `userId`, `role`, `accessToken`,
`tokenType` et `expiresIn`. Réutiliser le jeton pour vérifier l'identité :

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8080/api/v1/auth/me" `
    -Headers @{ Authorization = "Bearer $($session.accessToken)" }
```

Pour arrêter PULSE en mode développement, utiliser `Ctrl+C` dans son terminal.

## Routes disponibles

Les mêmes routes sont exposées par la Mock API et relayées par PULSE.
En utilisation normale, les clients appellent l'adresse de PULSE :

| Méthode | Route | Rôle |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Transmet `email` et `password`; retourne l'identité et le jeton |
| `GET` | `/api/v1/auth/me` | Vérifie `Authorization: Bearer <accessToken>` et retourne l'identité |

Les réponses attendues par le contrat incluent `200`, `400`, `401`, `403` et
`503`. PULSE relaie le statut et le corps JSON de la Mock API. Si PULSE ne peut
pas joindre cette API, il retourne `503 AUTH_SERVICE_UNAVAILABLE`.

La Mock API propose aussi des outils de simulation, hors routes d'authentification :

- `GET /simulator/unavailable` : lit l'état de simulation.
- `POST /simulator/unavailable` avec `{"enabled": true}` ou `false` : active ou désactive l'indisponibilité.
- L'en-tête `X-Simulate-Unavailable: true` simule une panne pour un appel d'authentification.
- La variable `SIMULATE_UNAVAILABLE=true` active la panne au démarrage.

## Lancer les tests

Les tests Python de `Mock` utilisent un faux client Supabase en mémoire. Ils
ne requièrent pas d'identifiants Supabase et ne vérifient pas la connexion au
projet réel :

```powershell
# Depuis la racine du dépôt
Set-Location .\Mock
python -m pip install -r requirements.txt
python -m pytest -q
```

Les tests Java vérifient le relais HTTP avec des réponses simulées. Les lancer
depuis la racine du dépôt, dans un nouveau terminal :

```powershell
Set-Location .\pulse
.\mvnw.cmd test
```

Une connexion réelle doit être vérifiée en démarrant les services et en
effectuant un appel de connexion avec un utilisateur existant dans Supabase.

## Dépannage

| Symptôme | Vérifications et solution |
|---|---|
| `docker compose` ne répond pas ou indique que le daemon est inaccessible | Démarrer Docker Desktop, attendre qu'il soit prêt, puis vérifier `docker info` et `docker compose version`. |
| Compose indique que `Mock/.env` est introuvable | Créer `Mock/.env` à la racine du dossier `Mock`, avec `SUPABASE_URL` et `SUPABASE_SECRET_KEY` (ou `SUPABASE_SERVICE_ROLE_KEY`). Relancer la commande Compose depuis la racine du dépôt. |
| La Mock API ne démarre pas | Vérifier `docker compose -f Mock/docker/docker-compose.yml ps`, puis lire `docker compose -f Mock/docker/docker-compose.yml logs --tail 100 mock-auth-api`. Vérifier que les deux variables Supabase sont définies ensemble. |
| `localhost:5000` refuse la connexion | Vérifier que le conteneur est démarré avec `docker compose ... ps`. Si le port hôte 5000 est déjà pris, choisir un autre `API_PORT` et utiliser ce même port dans `PULSE_AUTH_API_BASE_URL`. |
| PULSE ne démarre pas car le port 8080 est occupé | Fermer le service qui utilise ce port ou définir `$env:SERVER_PORT = "8081"` avant `.\mvnw.cmd spring-boot:run`, puis appeler PULSE sur `http://localhost:8081`. |
| La réponse est `503 AUTH_SERVICE_UNAVAILABLE` | Lire les logs de la Mock API. Vérifier l'URL Supabase, la clé serveur, la connectivité réseau, ainsi que l'existence de la table et des colonnes attendues. Pour le `503` émis par PULSE, vérifier aussi `PULSE_AUTH_API_BASE_URL`. |
| La réponse est `401 AUTH_INVALID_CREDENTIALS` | Vérifier l'adresse et le mot de passe d'un compte existant. L'adresse est recherchée sans tenir compte de la casse; un email inconnu et un mauvais mot de passe ont volontairement la même réponse. |
| La réponse est `401 AUTH_INVALID_TOKEN` | Envoyer le jeton complet reçu à la connexion avec le schéma `Bearer`, dans l'en-tête `Authorization`. |
| La réponse est `403 AUTH_ACCOUNT_DISABLED` | Le compte est désactivé dans la table `utilisateur`; seules les personnes responsables des données peuvent corriger son statut. |
| La réponse est `400 AUTH_BAD_REQUEST` | Envoyer un corps JSON avec les deux chaînes `email` et `password` et `Content-Type: application/json`. |
| PULSE ne rejoint pas la Mock API | Si PULSE s'exécute sur l'hôte, utiliser `http://localhost:5000` (ou le port configuré). Depuis un autre conteneur, ne pas utiliser `localhost`; configurer une adresse accessible depuis ce conteneur. |
| `mvnw.cmd` échoue ou Java n'est pas détecté | Vérifier `java -version` et que le JDK 17+ est installé et accessible dans `PATH`/`JAVA_HOME`. Le wrapper peut nécessiter Internet lors du premier lancement pour télécharger Maven et les dépendances. |
| Les tests passent mais la vraie connexion échoue | Les tests ne contactent pas Supabase ni l'API déployée. Vérifier les variables d'environnement et tester manuellement l'endpoint de connexion avec un utilisateur existant. |

## Documentation complémentaire

- [Guide de la Mock API](Mock/README.md)
- [Communication d'authentification côté PULSE](pulse/README.md)
- [Index de la documentation fonctionnelle et technique](docs/README.md)
- [Contrat du simulateur d'authentification](docs/auth-simulator.md)