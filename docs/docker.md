# Docker

The databases, the API, the frontend and a few tools run with [Docker Compose](https://docs.docker.com/compose/),
defined in [`docker-compose.yml`](../docker-compose.yml). The Dockerfiles are in [`deploy/`](../deploy).

## Services

| Service         | Container          | Host port | Container port | Profile    | Image / Dockerfile                                                  |
|-----------------|--------------------|----------:|---------------:|------------|---------------------------------------------------------------------|
| `api`           | `api`              | 1002      | 8001           | prod       | [`api.Dockerfile`](../deploy/api.Dockerfile)                        |
| `frontend`      | `frontend`         | 3030      | 3000           | prod       | [`frontend.Dockerfile`](../deploy/frontend.Dockerfile) (dev server) |
| `mariadb`       | `mariadb-database` | 2001      | 3306           | prod       | [`db/mariadb.Dockerfile`](../deploy/db/mariadb.Dockerfile)          |
| `phpmyadmin`    | `phpmyadmin`       | 2011      | 80             | prod       | [`db/phpmyadmin.Dockerfile`](../deploy/db/phpmyadmin.Dockerfile)    |
| `mongodb`       | `mongodb-database` | 2002      | 27017          | prod       | [`db/mongodb.Dockerfile`](../deploy/db/mongodb.Dockerfile)          |
| `mongo-express` | `mongo-express`    | 2022      | 8081           | prod       | [`db/mongoexpress.Dockerfile`](../deploy/db/mongoexpress.Dockerfile) |
| `qdrantdb`      | `qdrant-database`  | 2003      | 6333           | prod       | [`db/qdrantdb.Dockerfile`](../deploy/db/qdrantdb.Dockerfile)        |
| `portainer`     | `portainer`        | 1000      | 9000           | prod       | [`portainer.Dockerfile`](../deploy/portainer.Dockerfile)            |
| `utils`         | `utils`            | –         | –              | dev, debug | [`utils.Dockerfile`](../deploy/utils.Dockerfile)                    |

All services share the network `sdg-tag-heroes-net` (`10.5.0.0/24`) with fixed IP addresses. Inside the network,
containers reach each other by service or container name, for example `mariadb:3306`.

The dataset scripts do not run in a container; see [Building the dataset](dataset.md#running-the-scripts). The
production image of the frontend ([`frontend.prod.Dockerfile`](../deploy/frontend.prod.Dockerfile)) is not part of
the Compose file; see the [frontend README](../frontend/README.md#production).

## Volumes

| Service    | Host path                            | Container path     | Content                                       |
|------------|--------------------------------------|--------------------|-----------------------------------------------|
| `api`      | `api/`, `models/`, `db/`, `schemas/`, `request_models/`, `services/`, `settings/`, `enums/`, `utils/` | same names under `/` | The code, so the API reloads on every change |
| `api`      | `data/api/`                          | `/data/api`        | UMAP models                                   |
| `api`      | `data/docker/logs/`                  | `/logs`            | Log files                                     |
| `mariadb`  | `data/docker/db/mariadb/mysql-data/` | `/var/lib/mysql`   | Database files                                |
| `mongodb`  | `data/docker/db/mongodb/mongodb-data/` | `/data/db`       | Database files                                |
| `qdrantdb` | `data/docker/db/qdrantdb/storage/`   | `/qdrant/storage`  | Collections and snapshots                     |
| `frontend` | `frontend/`                          | `/app`             | The code; `node_modules` and `.nuxt` stay in the container |
| `utils`    | `data/db/`                           | `/workspace`       | Backups to restore                            |

## Common commands

Start the application (databases, API and their UIs):

```bash
docker compose up -d --build api mariadb phpmyadmin mongodb mongo-express qdrantdb
```

Start everything in the `prod` profile, including the frontend and Portainer:

```bash
docker compose --profile prod up -d --build
```

Follow the logs of a service:

```bash
docker compose logs -f api
```

Open a shell in a container:

```bash
docker compose exec api bash
```

Rebuild the frontend with fresh `node_modules`, after `frontend/package.json` changed:

```bash
docker compose up -d --build --force-recreate -V frontend
```

Stop everything (the data in `data/docker/` stays):

```bash
docker compose down
```

## Cleaning up

Docker images, build caches and unused volumes can fill the disk of Docker's virtual machine; the databases then fail
with "No space left on device". Show what uses the space:

```bash
docker system df
```

Remove the build cache and dangling images, which are safe to delete:

```bash
docker builder prune
```

```bash
docker image prune
```

> [!CAUTION]
> `docker system prune -a --volumes` also deletes unused images and volumes of **other** projects. Read what it lists
> before you confirm.
