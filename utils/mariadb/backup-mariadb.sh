#!/bin/bash

# Load environment variables
source ./env/mariadb.env
echo "Database: $MARIADB_HOST_LOCAL_IP"

# Perform the database dump
/usr/local/bin/mysqldump ${MARIADB_DATABASE} \
  --result-file=./${MARIADB_DATABASE}_mariadb_container-$(date +"%Y_%m_%d_%H_%M_%S")-dump.sql \
  --user=${MARIADB_USER} \
  --password=${MARIADB_PASSWORD} \
  --host=${MARIADB_HOST_LOCAL_IP} \
  --port=${MARIADB_PORT_LOCAL} \
  --column-statistics=0
