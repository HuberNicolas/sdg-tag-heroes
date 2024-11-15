# Database Connections

## How to connect

### Mariadb (via phpMyAdmin):
- URL: [http://localhost:2011/](http://localhost:2011/)
- Server: `MARIADB_HOST`
- Username: `MARIADB_USER`
- Password: `MARIADB_USER_PW`

### Mongodb (via Mongo-Express):
- URL: [http://localhost:2022/](http://localhost:2022/)
- Username: `ME_CONFIG_BASICAUTH_USERNAME`
- Password: `ME_CONFIG_BASICAUTH_PASSWORD`

### Qdrant (via dashboard):
- URL: [http://localhost:2003/dashboard](http://localhost:2003/dashboard)

### Couchdb (via Fauxton):
- URL: [http://localhost:2004/_utils/#](http://localhost:2004/_utils/#)
- Username: `COUCHDB_USER`
- Password: `COUCHDB_PASSWORD`

### Redis (via Redis Insight):
- URL: [http://localhost:2055/](http://localhost:2055/)
- Add Database Manually:
  - Host: `REDIS_HOST`
  - Port: `REDIS_PORT`
  - Database Alias: SDG (name does not matter)
  - Username: `REDIS_USER`
  - Password: `REDIS_USER-PW`
  - Timeout: 30

## MongoDB Backup and Restore Instructions

This guide provides instructions for backing up and restoring your MongoDB databases `sdg_database_clusters` and `sdg_explanations` using Docker with authentication.

### Prerequisites
- Ensure that your `mongodb-database` container is running.
- You have the necessary MongoDB credentials (username and password).

### Backup

You can use `mongodump` to create a backup of your MongoDB databases. Use the following commands:

```bash
# Backup sdg_database_clusters
docker exec -it mongodb-database mongodump --db sdg_database_clusters \
  --username <username> --password <password> --authenticationDatabase admin --out /data/backup

# Backup sdg_explanations
docker exec -it mongodb-database mongodump --db sdg_explanations \
  --username <username> --password <password> --authenticationDatabase admin --out /data/backup
```

- Replace `<username>` and `<password>` with your MongoDB credentials.
- The backups will be stored in the `/data/backup` directory inside the container.

#### Copy the Backup to Your Local Machine

```bash
docker cp mongodb-database:/data/backup ./data/db/backup
```

This command will copy the backup from the container to your local `./data/db/backup` directory.

### Restore

To restore your MongoDB databases using `mongorestore`, follow these steps:

#### Copy the Backup to the MongoDB Container

```bash
docker cp ./data/db/backup mongodb-database:/data/backup
```

#### Run the `mongorestore` Command

```bash
# Restore sdg_database_clusters
docker exec -it mongodb-database mongorestore --db sdg_database_clusters \
  --username <username> --password <password> --authenticationDatabase admin /data/backup/sdg_database_clusters

# Restore sdg_explanations
docker exec -it mongodb-database mongorestore --db sdg_explanations \
  --username <username> --password <password> --authenticationDatabase admin /data/backup/sdg_explanations
```

- Replace `<username>` and `<password>` with your MongoDB credentials.
