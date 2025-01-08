import time
from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models.publications.publication import Publication
from models.request import PublicationIdsRequest
from services.publication_summary import PublicationSummaryService
from settings.settings import SummaryRouterSettings
summary_router_settings = SummaryRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(SummaryRouterSettings.SUMMARY_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/summaries",
    tags=["summaries"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Instantiate the service
service = PublicationSummaryService()

@router.post("/summarize")
async def summarize_by_ids(
        request: PublicationIdsRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> Dict:
    """
    Summarize abstracts for a list of publication IDs.
    """
    # Authenticate user
    user = verify_token(token, db)

    # Query publications by IDs
    publications = db.query(Publication).filter(Publication.publication_id.in_(request.publication_ids)).all()

    # Extract abstracts
    abstracts = [pub.description for pub in publications if pub.description]

    # Summarize abstracts
    summaries = service.summarize_publications(abstracts)
    return {"summaries": summaries}



@router.post("/generate_keywords")
async def extract_keywords_by_ids(
        request: PublicationIdsRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> Dict:
    """
    Extract keywords from abstracts for a list of publication IDs.
    """
    # Authenticate user
    user = verify_token(token, db)

    # Query publications by IDs
    publications = db.query(Publication).filter(Publication.publication_id.in_(request.publication_ids)).all()

    # Extract abstracts
    abstracts = [pub.description for pub in publications if pub.description]

    # Extract keywords
    keywords = service.extract_keywords(abstracts)
    return {"keywords": keywords}
