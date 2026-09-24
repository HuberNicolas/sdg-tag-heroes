# Docker container

## Container overview

| Service       | Container Name   | Port (Outside) | Port (Container) | Description                     |
|---------------|------------------|----------------|------------------|---------------------------------|
| portainer     | portainer        | 1000           | 9000             | Docker container management UI  |
| api           | api              | 1002           | 8001             | API (FastAPI)                   |
| mariadb       | mariadb-database | 2001           | 3306             | MariaDB SQL database            |
| phpmyadmin    | phpmyadmin       | 2011           | 80               | phpMyAdmin UI for MariaDB       |
| mongodb       | mongodb-database | 2002           | 27017            | MongoDB database                |
| mongo-express | mongo-express    | 2022           | 8081             | Mongo Express UI                |
| qdrantdb      | qdrant-database  | 2003           | 6333             | Qdrant vector search engine     |
| frontend      | frontend         | 3030           | 3000             | Frontend application (Nuxt)     |
| utils         | utils            | –              | –                | Shell with database client tools |

The dataset scripts run on the host, not in a container (see "Running the scripts" in the README).


Stop all the containers

```bash
docker stop $(docker ps -a -q)
```

Remove all the containers

```bash
docker rm $(docker ps -a -q)
```


```bash
docker system prune -a
```


## Information
- entrypoint: Defines the executable that will always run in the container. It can be combined with the CMD field, which provides arguments to the entrypoint.

- command: Overrides the default command provided by the image. It can replace both entrypoint and CMD or just override CMD if no entrypoint is set.
