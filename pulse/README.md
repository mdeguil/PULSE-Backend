# PULSE Backend — communication avec l'API d'authentification

## Rôle du backend

Le backend Java PULSE sert de relais entre le client et la Mock API HAC. Il ne
vérifie pas lui-même les mots de passe et ne se connecte pas à Supabase :
la Mock API reçoit les identifiants, interroge la table `utilisateur` et
retourne le résultat. Les secrets Supabase restent configurés côté Mock API.

## Parcours d'authentification

1. Le client envoie `POST /api/v1/auth/login` au backend PULSE avec un JSON
   contenant `email` et `password`.
2. `AuthController` transmet la requête à `AuthApiClient`, qui appelle
   `POST /api/v1/auth/login` sur la Mock API.
3. Le backend relaie au client le statut HTTP et le corps JSON de la réponse.
   En cas de succès, celui-ci contient notamment `accessToken`, `tokenType`
   et `expiresIn`. En cas d'échec, le code et le message d'erreur de l'API
   sont conservés.
4. Pour consulter l'identité, le client envoie
   `GET /api/v1/auth/me` au backend avec
   `Authorization: Bearer <accessToken>`. PULSE transmet cet en-tête à la
   Mock API et relaie sa réponse.

Le backend ne stocke pas le jeton et ne remplace pas l'authentification de
l'API amont. Le jeton de démonstration est actuellement au format
`demo-token-<userId>`.

## Adresse de l'API amont

L'URL de base est configurée par la propriété Spring
`pulse.auth-api.base-url`, définie à partir de la variable
`PULSE_AUTH_API_BASE_URL`. Elle ne doit contenir que l'origine de l'API;
les chemins `/api/v1/auth/login` et `/api/v1/auth/me` sont ajoutés par le
client HTTP.

- **Exécution locale hors Docker** : la valeur par défaut est
  `http://localhost:5000`. La Mock API doit être lancée et accessible sur ce
  port avant d'essayer de se connecter.
- **Mock API dans Docker, PULSE sur l'hôte** : utiliser
  `http://localhost:5000`, qui est la valeur par défaut. Le Compose de la Mock
  API ne démarre que celle-ci; le backend PULSE doit être lancé séparément.
- **Déploiement séparé** : définir `PULSE_AUTH_API_BASE_URL` à l'URL de la
  Mock API joignable depuis l'environnement où tourne PULSE.

Dans un conteneur, `localhost` désigne ce même conteneur. Ne pas configurer
`http://localhost:5000` pour joindre un autre conteneur; utiliser une adresse
joignable depuis le conteneur, comme `http://host.docker.internal:5000` sous
Docker Desktop, ou l'adresse réseau configurée pour le déploiement.

## Démarrage et vérification

La Mock API peut être démarrée seule avec Docker, depuis la racine du dépôt :

```powershell
docker compose -f Mock/docker/docker-compose.yml up --build -d
```

Pour lancer le backend Java séparément, depuis le dossier `pulse` :

```powershell
$env:PULSE_AUTH_API_BASE_URL = "http://localhost:5000"
.\mvnw.cmd spring-boot:run
```

Le client appelle PULSE sur `http://localhost:8080`; la Mock API est
accessible depuis l'hôte sur `http://localhost:5000`. Pour lancer PULSE dans
un conteneur séparé, configurez `PULSE_AUTH_API_BASE_URL` vers une adresse
accessible depuis ce conteneur.

Exemple de connexion au backend :

```http
POST http://localhost:8080/api/v1/auth/login
Content-Type: application/json

{"email":"utilisateur@example.com","password":"mot-de-passe"}
```

Puis envoyer le jeton retourné lors de la vérification d'identité :

```http
GET http://localhost:8080/api/v1/auth/me
Authorization: Bearer demo-token-<userId>
```

## Gestion des erreurs

Les réponses d'authentification de la Mock API, notamment `400`, `401`,
`403` et `503`, sont relayées au client avec leur corps JSON. Si PULSE ne peut
pas joindre l'API amont, il retourne `503 AUTH_SERVICE_UNAVAILABLE`. Une
requête illisible ou sans les champs requis est rejetée avec
`400 AUTH_BAD_REQUEST`.

Le relais HTTP est implémenté dans
`src/main/java/com/pulse/backend/controller/AuthController.java` et
`src/main/java/com/pulse/backend/service/AuthApiClient.java`. La traduction
des erreurs locales est dans
`src/main/java/com/pulse/backend/controller/AuthApiExceptionHandler.java`.
