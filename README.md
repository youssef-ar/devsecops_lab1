# TP 1 — SAST et SCA (état initial volontairement vulnérable)

Ce dépôt fournit une application Flask minimale et son infrastructure Docker pour réaliser le TP. **Cette version est l'état avant corrections** : les vulnérabilités sont présentes volontairement afin que les scans produisent un rapport exploitable.

## Pré-requis

- Git
- Docker avec le plugin Docker Compose

## 1. Démarrer l'application

Définir les secrets avant de démarrer les conteneurs lorsque cela est possible. Ne jamais les committer dans Git :

```bash
export FLASK_SECRET_KEY="$(openssl rand -hex 32)"
export NVD_API_KEY="votre_cle_nvd"
```

`FLASK_SECRET_KEY` est recommandé pour conserver la même clé entre les redémarrages. Si elle n'est pas définie, l'application génère une clé aléatoire au démarrage ; les commandes Docker comme `docker compose down` restent ainsi utilisables sans variable d'environnement.

```bash
docker compose build
docker compose up -d app
```

L'application est disponible sur <http://localhost:5000>.

Endpoints de démonstration :

- `/health` : contrôle de santé
- `/users?name=Alice` : recherche utilisateur (construction SQL non sûre et rendu HTML non sûr)
- `/diagnostics?command=echo%20hello` : exécution de diagnostic non sûre

Pour observer les logs :

```bash
docker compose logs -f app
```

## 2. Scan SAST avec SonarQube

Le service `sonarqube` démarre le serveur SonarQube sur <http://localhost:9000>. Le premier démarrage peut prendre une à deux minutes :

```bash
docker compose --profile scan up -d sonarqube
```

Ouvrir SonarQube, se connecter avec `admin` / `admin`, changer le mot de passe si demandé, puis créer un token utilisateur dans **My Account → Security**. Exporter ensuite ce token dans le terminal :

```bash
export SONAR_TOKEN="votre_token_sonarqube"
```

Lancer l'analyse depuis le conteneur scanner :

```bash
docker compose --profile scan run --rm sonar-scanner
```

Consulter le projet `devsecops-tp1` dans SonarQube et relever au minimum deux problèmes de sécurité. Dans le compte-rendu, noter la règle, la gravité, le fichier, la ligne et le risque. Les règles exactes dépendent de la version de SonarQube et de son analyseur Python.

## 3. Scan SCA avec OWASP Dependency-Check

Dependency-Check est l'outil SCA utilisé pour ce TP. La version actuelle nécessite une clé API NVD pour télécharger une nouvelle base CVE. Créer une clé gratuite sur <https://nvd.nist.gov/developers/request-an-api-key>, puis l'exporter :

```bash
export NVD_API_KEY="votre_cle_nvd"
```

La configuration refuse maintenant de démarrer si cette variable n'est pas définie, au lieu de lancer un téléchargement avec une clé vide.

```bash
docker compose --profile scan run --rm dependency-check
```

Les rapports HTML, JSON et XML sont créés dans `reports/dependency-check/`. Le premier lancement peut être long car la base CVE est téléchargée.

Si une première tentative a échoué pendant la mise à jour de la base, supprimer uniquement le volume de cache Dependency-Check puis relancer :

```bash
docker compose down
docker volume rm devsecops_dependency-check-data 2>/dev/null || true
mkdir -p reports/dependency-check
docker compose --profile scan run --rm dependency-check
```

La dépendance `requests==2.19.1` est volontairement ancienne. Le service scanne directement `/src/requirements.txt` et active l'analyseur Python expérimental ; cela est nécessaire pour éviter un rapport indiquant `Dependencies Scanned: 0`. Vérifier dans le rapport les CVE associées et expliquer pourquoi une version corrigée doit être utilisée plutôt que de masquer le résultat.

## 4. Corrections SAST appliquées

- La protection CSRF est activée globalement avec `Flask-WTF` et une clé secrète fournie par `FLASK_SECRET_KEY`.
- La base SQLite n'est plus créée dans `/tmp` ; elle est stockée dans `/data` dans le conteneur, ou dans `data/` en exécution locale.
- L'application utilise `127.0.0.1` par défaut. Le service Docker fournit explicitement `HOST=0.0.0.0` afin que le port publié soit accessible depuis l'hôte ; cette exception est limitée au déploiement conteneurisé.

Reconstruire après modification :

```bash
docker compose down
docker compose build --no-cache app
docker compose up -d app
```

## 5. Démonstration attendue avant correction

1. Montrer l'état initial du dépôt et les versions de `requirements.txt`.
2. Démarrer l'application et présenter les endpoints.
3. Exécuter les deux scans et conserver les rapports dans `reports/`.
4. Sélectionner au moins deux problèmes SAST SonarQube et une dépendance vulnérable.
5. **Ne pas appliquer les corrections dans cette étape** : elles constituent la suite du TP.

## Structure

- `app.py` : application Flask volontairement vulnérable
- `requirements.txt` : dépendances volontairement obsolètes
- `Dockerfile` : image de l'application
- `docker-compose.yml` : application, SonarQube, scanner et SCA
- `reports/` : rapports Dependency-Check générés localement (ignorés par Git)

## Nettoyage

```bash
docker compose down -v
```
