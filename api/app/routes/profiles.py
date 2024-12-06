import time
from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import SkillsRequest, InterestsRequest
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


from services.user_query_generator import SkillsQueryResponse, UserQueryGenerator, InterestsQueryResponse

from settings.settings import ProfileRouterSettings
profiles_router_settings = ProfileRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(profiles_router_settings.PROFILES_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
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

@router.post(
    "/skills",
    response_model=SkillsQueryResponse,
    description="Generate an User query based on the user's skills or knowledge."
)
async def generate_skills_query(
    request: SkillsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> SkillsQueryResponse:
    """
    Generate an User query based on the user's skills or existing knowledge.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    try:
        # Initialize the query generator
        query_generator = UserQueryGenerator()

        # Generate the query and return the response
        return query_generator.generate_skills_description(request.skills)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate skills-based description: {str(e)}"
        )

@router.post(
    "/interests",
    response_model=InterestsQueryResponse,
    description="Generate an SDG query based on the user's interests or aspirations."
)
async def generate_interests_query(
    request: InterestsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> BaseModel:
    """
    Generate an User query based on the user's interests or aspirations.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    try:
        # Initialize the query generator
        query_generator = UserQueryGenerator()

        # Generate the query and return the response
        return query_generator.generate_interests_description(request.interests)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interests-based description: {str(e)}"
        )
