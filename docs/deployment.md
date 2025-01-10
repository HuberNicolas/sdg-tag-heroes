use bash instead of sh where possible -> autocomplete
docker exec -it utils bash

Access Mongo-Express
ssh -N -D 8080 <deployer@herold.ifi.uzh.ch>

Firefox: <http://10.5.0.9:8081>

Run containers
docker compose up api frontend mariadb phpmyadmin mongodb mongo-express qdrantdb

Restoring:
Copy files into /home/deployer/sdg-tag-heroes/data/db

Restore Mongodb
folder sdg_explanations, inside .bson and .metadata.json

docker exec -it utils mongorestore --host 10.5.0.8 --port 27017 \
  --username <mongodb-user> --password <mongodb-user-pw> \
  --authenticationDatabase admin /workspace/sdg_explanations

// here we use the name of the contaienr, was we can talk from container to container
docker exec -it utils mongosh "mongodb://<mongodb-user>:<mongodb-user-pw>@10.5.0.8:27017/admin"

Restore Qdrant
docker exec -it utils bash /workspace/restore-qdrant.sh /workspace/publications-mt-4595442005324815-2024-11-15-13-46-47.snapshot

basically is a curl response to
again containername
<http://qdrant-database:6333/collections/publications-mt/snapshots/upload>

Restoring mariadb
// did not work when i initially created the container

docker exec -it utils bash mariadb -h mariadb-database -u root -p igcl < /workspace/igcl_dump.sql

docker exec -it utils bash
mariadb -h mariadb-database -u root -p
