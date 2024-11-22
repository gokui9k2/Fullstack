# Projet UFC Analytics : Une Application Fullstack Conteneurisée

## Introduction

Le projet **UFC Analytics** vise à développer une application fullstack conteneurisée permettant d’analyser des données sur l’Ultimate Fighting Championship (UFC). Il combine une interface utilisateur réalisée en Flask, une API construite avec **FastAPI**, une base de données PostgreSQL pour le stockage des données, et Elasticsearch pour des recherches avancées.

L’objectif est de fournir un outil interactif permettant de visualiser, rechercher et analyser des données sur les combats, les combattants et les événements UFC.

---

## Guide Utilisateur

Pour lancer cette application, il faut exécuter les commandes suivantes dans le terminal :

```bash
docker-compose build
docker-compose up
```



### Voici une petite aperçu de notre application: 

[Watch the video](https://youtu.be/4NgM59sO4DM)

## Fonctionnalités Principales

1. **Authentification JWT** : 
   - Inscription et connexion avec stockage sécurisé des mots de passe grâce à Flask-SQLAlchemy.
   - Génération et vérification de tokens JWT pour sécuriser l'accès à certaines API.

2. **API sécurisée avec FastAPI** :
   - Récupération des données des combattants via des endpoints sécurisés.
   - Gestion des erreurs HTTP (401, 403, 404) et typage rigoureux pour tous les endpoints.

3. **Visualisations Avancées** :
   - Utilisation de React avec Chart.js pour afficher des heatmaps, des graphiques de ratios de victoires, des distributions par catégorie de poids, etc.

4. **Base de données PostgreSQL** :
   - Intégration d’un schéma robuste contenant une table `User` pour la gestion des utilisateurs et une table `ufctable` pour les données UFC.

5. **Intégration Elasticsearch** :
   - Indexation des données pour permettre des recherches performantes avec des fonctionnalités avancées comme le fuzzy search.

---

## Technologies Utilisées

### Backend

#### **FastAPI : API REST sécurisée**
Nous avons utilisé **FastAPI** pour concevoir une API REST sécurisée et performante. Cette technologie a permis de structurer des endpoints robustes et bien typés, avec des fonctionnalités d’authentification utilisant des tokens JWT. Parmi les endpoints développés, certains sont accessibles uniquement après authentification, comme celui qui permet de récupérer les données des combattants UFC. La gestion des erreurs HTTP a été intégrée pour garantir une communication claire entre le frontend et l'API, en évitant les erreurs serveur non contrôlées (erreurs 500). Enfin, l’utilisation de FastAPI a permis de tirer parti des annotations Python pour un typage strict, améliorant ainsi la lisibilité et la maintenabilité du code.

#### **PostgreSQL : Stockage des données**
Le choix de **PostgreSQL** s’est imposé pour son efficacité et sa compatibilité avec notre projet. La base de données est utilisée pour stocker des informations critiques, comme les détails des combattants et les comptes utilisateurs. Une table `User` a été implémentée pour gérer les utilisateurs et leurs mots de passe, ces derniers étant hashés pour assurer la sécurité des données sensibles. Une autre table, `ufctable`, regroupe les données analytiques sur les combats UFC. Nous avons également intégré un script Python asynchrone pour insérer automatiquement des données issues de fichiers CSV dans PostgreSQL au démarrage, garantissant ainsi un lancement sans intervention manuelle.

#### **Elasticsearch : Recherche avancée**
**Elasticsearch** a été intégré pour offrir des capacités de recherche avancée et rapide sur les données UFC. Les données issues de PostgreSQL ont été indexées dans Elasticsearch grâce à un pipeline automatisé, permettant aux utilisateurs d’effectuer des recherches complexes, comme des correspondances floues ou des recherches par préfixes. Par exemple, un utilisateur peut rechercher un combattant en saisissant seulement une partie de son nom, et Elasticsearch retourne les résultats les plus pertinents. Ce système offre une expérience utilisateur fluide et performante, en complément des fonctionnalités analytiques de l’application.

---

### Frontend

#### **Flask : Serveur web et intégration des visualisations**
Le framework **Flask** a été utilisé pour créer un serveur web léger mais puissant, servant de passerelle entre l’utilisateur et les services backend. Flask gère les routes pour les pages principales, comme l’inscription, la connexion et le tableau de bord d’analyse. 

Nous avons intégré **React Chart.js** pour afficher des visualisations interactives basées sur les données fournies par l’API backend. Ces graphiques, tels que des heatmaps et des courbes, permettent aux utilisateurs de mieux comprendre les performances des combattants ou la répartition des résultats. Flask a également été configuré pour rendre ces visualisations dynamiques, en actualisant les données au fur et à mesure des interactions des utilisateurs, garantissant ainsi une expérience fluide et réactive.

---

### Conteneurisation

#### **Docker et Docker Compose : pour orchestrer tous les services**
Pour assurer un déploiement simple et fiable, nous avons utilisé **Docker** pour conteneuriser chaque composant du projet, et **Docker Compose** pour orchestrer ces différents services. Chaque service – frontend (Flask), backend (FastAPI), base de données PostgreSQL, et Elasticsearch – fonctionne dans un conteneur isolé, ce qui garantit leur indépendance et facilite le développement et le déploiement.

Le fichier `docker-compose.yml` gère la coordination des services en définissant les dépendances (par exemple, le backend dépend de PostgreSQL et Elasticsearch). Nous avons également intégré des scripts d’attente (`wait-for-api.sh` et `script.sh`) pour s’assurer que les services critiques, comme la base de données et l’API, sont prêts avant de démarrer les autres conteneurs. Cette orchestration garantit que l’ensemble de l’application peut être lancé avec une seule commande (`docker-compose up`), rendant le processus transparent et reproductible sur n’importe quel environnement.

### Test unitaire : 

Pour finir ce projet, nous avons décidé d'effectuer des tests unitaires. Malheureusement, nous n'avons pas réussi à faire tous les tests que nous voulions. Il est généralement préférable de réaliser des tests unitaires pendant le développement, mais dans notre cas, nous les avons effectués après la création de l'application. Cependant, nous avons tout de même pu réaliser certains de ces tests, comme celui du login, entre autres.

Pour effectuer ces tests, il faut entrer dans le conteneur api comme ceci :

```bash
docker exec -it full_stack-api-1 /bin/sh
```

## Conclusion

Ce projet met en œuvre une architecture fullstack moderne, avec une attention particulière à la sécurité, à la performance et à l’expérience utilisateur. Grâce à la conteneurisation et à l’orchestration, l’application est prête pour une utilisation professionnelle ou académique. Nous espérons qu’elle reflète notre maîtrise des concepts étudiés tout en offrant une base solide pour des améliorations futures.
