import os

from fastapi import FastAPI

from db.couchdb_connector import client as cclient
from db.mariadb_connector import conn as mconn
from db.mongodb_connector import client as mclient
from db.qdrantdb_connector import client as qclient


def in_docker():
    return os.environ.get("IN_DOCKER") == "true"


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, Pipeline!"}
