# Docker container

## Container overview
| Service       | Container Name   | Port (Outside) | Port (Container) | Description                           |
|---------------|------------------|----------------|------------------|---------------------------------------|
| portainer     | portainer        | 1000           | 9000             | Docker container management UI        |
| api           | api              | 1001           | 8000             | API service                           |
| backend       | backend          | 1002           | 8001             | Backend service                       |
| pipeline      | pipeline         | 1003           | 8000             | Pipeline service                      |
| mongodb       | mongodb-database | 2001           | 27017            | MongoDB database                      |
| mongo-express | mongo-express    | 2011           | 8081             | MongoDB Express UI                    |
| mariadb       | mariadb-database | 2002           | 3306             | MariaDB SQL database                  |
| phpmyadmin    | phpmyadmin       | 2022           | 80               | PHPMyAdmin UI for MariaDB             |
| qdrantdb      | qdrant-database  | 2003           | 6333             | Qdrant vector search engine           |
| couchdb       | couchdb-database | 2004           | 5984             | CouchDB NoSQL database                |
| redisdb       | redisdb-database | 2005           | 6379             | Redis key-value store                 |
| redis-insight | redis-insight    | 2055           | 5540             | RedisInsight management UI            |
| frontend      | frontend         | 3030           | 3000             | Frontend application (Nuxt.js)        |
| prefect       | prefect-server   | 4040           | 4000             | Prefect workflow orchestration server |


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
