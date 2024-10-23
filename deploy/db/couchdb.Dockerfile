FROM couchdb:latest

COPY ./deploy/db/couchdb-local.ini /opt/couchdb/etc/local.d/local.ini
