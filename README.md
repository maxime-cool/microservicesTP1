# UE-AD-A1-REST

### Zuoyu Zhang & Maxime Garnier

#### nous avons faites le TP vert pour TP REST, nous allons expliquer comment démarrer notre application dans Docker: 

nécessité : 
- Docker
- Docker compose
- Git 

Processus :

1. Allez d'abord sur le site GitHub et téléchargez tout le code dont vous avez besoin à l'aide de la commande : `git clone https://github.com/maxime-cool/microservicesTP1.git`

2. Allez dans le dossier du code téléchargé dans le terminal : `cd microservicesTP1`

3. Dans le répertoire de projet, exécutez la commande `docker-compose build` pour construire les images Docker pour les services. Cette commande construira les images en fonction des fichiers Dockerfile spécifiés dans le fichier `docker-compose.yml`.

4. Lancer vos services : Une fois que les images sont construites, vous pouvez lancer vos services avec Docker Compose en utilisant la commande `docker-compose up`. Si vous souhaitez exécuter les services en arrière-plan, utilisez l'option `-d` : `docker-compose up -d`

5. Vérifiez l'état de vos services : Utilisez `docker-compose ps` pour vérifier l'état de vos services en cours d'exécution.

6. Vous pouvez arrêter les conteneurs avec `docker compose stop` ou les détruire avec `docker compose down`.
