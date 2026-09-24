# Deployment

How the application ran on a Linux server at UZH, from a clone of this repository, with Docker Compose. The steps
apply to any server with Docker.

## 1. Prepare the server

1. Install Docker with the Compose plugin.
2. Clone the repository, for example to `/home/deployer/sdg-tag-heroes`.
3. Create the environment files as in the [quick start](../README.md#2-create-the-environment-files). Use strong
   passwords and a new `SECRET_KEY`.
4. Set `API_URL` in `frontend/.env` to the address at which **browsers** reach the API.

## 2. Start the containers

```bash
docker compose up -d --build api frontend mariadb phpmyadmin mongodb mongo-express qdrantdb
```

The `frontend` service runs the Nuxt development server. For a public deployment, the production image is the
better choice; see the [frontend README](../frontend/README.md#production).

## 3. Restore the data

Copy the backups into `data/db/` on the server (for example with `scp` or `rsync`). The `utils` container mounts that
folder as `/workspace` and has the MariaDB and MongoDB client tools. Start it:

```bash
docker compose --profile debug up -d utils
```

Inside the Docker network, the databases are reached by container name. Replace the placeholders with the
credentials from `env/`.

**MariaDB:**

```bash
docker exec -i utils mariadb -h mariadb-database -u root -p igcl < data/db/igcl_dump.sql
```

**MongoDB** (a `mongodump` folder `sdg_explanations/` with `.bson` and `.metadata.json` files):

```bash
docker exec -it utils mongorestore --host mongodb-database --port 27017 --username <mongodb-user> --password <mongodb-password> --authenticationDatabase admin /workspace/sdg_explanations
```

**Qdrant:** [`restore-qdrant.sh`](../utils/qdrant/restore-qdrant.sh) uploads a snapshot to `qdrant-database:6333`:

```bash
docker exec -it utils bash /workspace/restore-qdrant.sh /workspace/<snapshot-file>.snapshot
```

Restart the API afterwards:

```bash
docker compose restart api
```

[Databases](databases.md#backup-and-restore) describes the same steps without the `utils` container.

## 4. Reach the admin UIs

phpMyAdmin, Mongo Express and the Qdrant dashboard should not be open to the internet. Reach them through an SSH
tunnel instead, as a SOCKS proxy:

```bash
ssh -N -D 8080 <user>@<server>
```

Set `localhost:8080` as the SOCKS proxy in the browser (Firefox: *Settings → Network Settings*). The containers are
then reachable at their network addresses, for example Mongo Express at <http://10.5.0.9:8081>.

## Tips

- Use `bash` rather than `sh` in the containers, for tab completion: `docker exec -it utils bash`.
- Connect to MongoDB from the `utils` container:

  ```bash
  docker exec -it utils mongosh "mongodb://<mongodb-user>:<mongodb-password>@mongodb-database:27017/admin"
  ```
