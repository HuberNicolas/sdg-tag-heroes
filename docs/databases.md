# Databases

The application uses three databases, each in its own container. This guide explains how to look into them, and how
to back them up and restore them.

| Database | Container          | Host port | Holds                                                         | Web UI                                              |
|----------|--------------------|----------:|---------------------------------------------------------------|-----------------------------------------------------|
| MariaDB  | `mariadb-database` | 2001      | Database `igcl`: publications, predictions, users, game state | phpMyAdmin at <http://localhost:2011>              |
| MongoDB  | `mongodb-database` | 2002      | Databases `sdg_explanations`, `sdg_database` and `sdg_database_clusters` | Mongo Express at <http://localhost:2022> |
| Qdrant   | `qdrant-database`  | 2003      | Collection `publications-mt`: publication embeddings          | Dashboard at <http://localhost:2003/dashboard>     |

Their data lives in `data/docker/db/` on the host.

## Contents

- [Web UIs](#web-uis)
- [Backup and restore](#backup-and-restore)
  - [MariaDB](#mariadb)
  - [MongoDB](#mongodb)
  - [Qdrant](#qdrant)
- [Start from empty databases](#start-from-empty-databases)

## Web UIs

| UI            | Log in with                                                                                             |
|---------------|---------------------------------------------------------------------------------------------------------|
| phpMyAdmin    | Server `mariadb`, and `MARIADB_USER` and `MARIADB_PASSWORD` from `env/mariadb.env` (or `root` and `MYSQL_ROOT_PASSWORD`) |
| Mongo Express | `ME_CONFIG_BASICAUTH_USERNAME` and `ME_CONFIG_BASICAUTH_PASSWORD` from `env/mongo-express.env`           |
| Qdrant        | No login                                                                                                |

## Backup and restore

The commands below run in the database containers, so you need no database tools on your machine. They read the
credentials from the container's environment. Run them from the repository root.

> [!TIP]
> A restore replaces the current contents. Stop the API first (`docker compose stop api`) and start it again
> afterwards, so it does not read half-restored data.

### MariaDB

Back up the database `igcl` into a SQL file:

```bash
docker exec mariadb-database sh -c 'mariadb-dump -u root -p"$MYSQL_ROOT_PASSWORD" igcl' > data/db/igcl_dump.sql
```

Restore it:

```bash
docker exec -i mariadb-database sh -c 'mariadb -u root -p"$MYSQL_ROOT_PASSWORD" igcl' < data/db/igcl_dump.sql
```

[`utils/mariadb/backup-mariadb.sh`](../utils/mariadb/backup-mariadb.sh) does the same backup with `mysqldump` on
your machine.

### MongoDB

The databases that matter are `sdg_explanations` (the explanations the API reads), `sdg_database` (the SDGs) and
`sdg_database_clusters` (the clusters, not used by the deployed version).

Back up a database into the container, then copy the dump to your machine:

```bash
docker exec mongodb-database sh -c 'mongodump -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --db sdg_explanations --out /tmp/backup'
```

```bash
docker cp mongodb-database:/tmp/backup ./data/db/backup
```

To back up only the collection the API reads, add `--collection explanations_scaled_new`.

Restore it: copy the dump into the container, then run `mongorestore`:

```bash
docker cp ./data/db/backup mongodb-database:/tmp/backup
```

```bash
docker exec mongodb-database sh -c 'mongorestore -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --db sdg_explanations --drop /tmp/backup/sdg_explanations'
```

`--drop` replaces collections that already exist.

### Qdrant

Qdrant backs up a collection as a snapshot, through its REST API.

Create a snapshot. The response contains its file name:

```bash
curl -X POST http://localhost:2003/collections/publications-mt/snapshots
```

Download it:

```bash
curl -o data/db/publications-mt.snapshot http://localhost:2003/collections/publications-mt/snapshots/<snapshot-name>
```

Restore it: upload the file, which replaces the collection:

```bash
curl -X POST 'http://localhost:2003/collections/publications-mt/snapshots/upload' -F 'snapshot=@data/db/publications-mt.snapshot'
```

[`utils/qdrant/restore-qdrant.sh`](../utils/qdrant/restore-qdrant.sh) does the same upload from the `utils` container
(see [Deployment](deployment.md#3-restore-the-data)).

## Start from empty databases

Stop the containers and delete their data:

```bash
docker compose down
```

```bash
bash utils/docker/delete-docker-data.sh
```

The script removes `data/docker/` with `sudo`, because the database containers create their files as root. The next
`docker compose up` starts with empty databases; fill them as described in the [README](../README.md#4-fill-the-databases).
