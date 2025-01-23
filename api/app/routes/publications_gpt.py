from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from models import Fact, Summary
from models.publications.publication import Publication
from schemas import FactSchemaFull
from api.app.routes.authentication import verify_token
from api.app.security import Security
from settings.settings import PublicationsRouterSettings
from requests_models.publications_gpt import PublicationIdsRequest
from utils.logger import logger
from schemas.gpt_assistant_service import (
    PublicationSummarySchema,
    PublicationsCollectiveSummarySchema,
    PublicationSDGAnalysisSchema,
    PublicationKeywordsSchema,
)
from services.gpt.gpt_assistant_service import GPTAssistantService


# Setup Logging
publications_router_settings = PublicationsRouterSettings()
logging = logger(publications_router_settings.PUBLICATIONS_ROUTER_LOG_NAME)

# Setup OAuth2 and security
security = Security()
oauth2_scheme = security.oauth2_scheme

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the API Router
router = APIRouter(
    prefix="/publications",
    tags=["Publications"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

# Use the GPT Assistant service for publication-centred operations
assistant = GPTAssistantService()

@router.get("/{publication_id}/explain/goal/{sdg_id}", response_model=PublicationSDGAnalysisSchema)
async def explain_publication_sdg_relevance(
    publication_id: int,
    sdg_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    sdg_goal_analysis = assistant.analyze_sdg(title=publication.title, abstract=publication.description, goal=str(sdg_id))
    return {**sdg_goal_analysis.model_dump(), "publication_id": publication_id, "title": publication.title ,"abstract": publication.description}

@router.get("/{publication_id}/explain/target/{target_id}", response_model=PublicationSDGAnalysisSchema)
async def explain_publication_sdg_target(
    publication_id: int,
    target_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    sdg_target_analysis = assistant.analyze_sdg(title=publication.title, abstract=publication.description, target=target_id)
    return {**sdg_target_analysis.model_dump(), "publication_id": publication_id,  "title": publication.title, "abstract": publication.description}


@router.get("/{publication_id}/keywords", response_model=PublicationKeywordsSchema)
async def extract_keywords(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    if not publication.title and not publication.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content available for keyword extraction")

    keywords = assistant.extract_keywords(title=publication.title, abstract=publication.description)
    return PublicationKeywordsSchema(publication_id=publication_id, keywords=keywords)


@router.get("/{publication_id}/facts", response_model=FactSchemaFull)
async def create_did_you_know_fact(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    existing_fact = db.query(Fact).filter(Fact.publication_id == publication_id).first()
    if existing_fact:
        return FactSchemaFull.model_validate(existing_fact)

    if not publication.title and not publication.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content available for fact generation")

    new_fact_content = assistant.create_fact(title=publication.title, abstract=publication.description)

    new_fact = Fact(content=new_fact_content, publication_id=publication_id)
    db.add(new_fact)
    db.commit()
    db.refresh(new_fact)

    return FactSchemaFull.model_validate(new_fact)


@router.get("/{publication_id}/summary", response_model=PublicationSummarySchema)
async def create_or_get_publication_summary(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    existing_summary = db.query(Summary).filter(Summary.publication_id == publication_id).first()
    if existing_summary:
        return PublicationSummarySchema(publication_id=publication_id, summary=existing_summary.content)

    if not publication.title and not publication.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content available for summary generation")

    new_summary_content = assistant.summarize_publication(title=publication.title, abstract=publication.description)

    new_summary = Summary(content=new_summary_content, publication_id=publication_id)
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return PublicationSummarySchema(publication_id=publication_id, summary=new_summary_content)


@router.post("/collective-summaries", response_model=PublicationsCollectiveSummarySchema)
async def create_collective_summary(
    request: PublicationIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token, db)
    publication_ids = request.publication_ids

    publications = db.query(Publication).filter(Publication.publication_id.in_(publication_ids)).all()
    if not publications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No publications found for the given IDs.")

    publication_data = [
        {"id": pub.publication_id, "title": pub.title or "", "abstract": pub.description or ""}
        for pub in publications
    ]

    collective_summary_response = assistant.summarize_publications(publications=publication_data)

    collective_summary = PublicationsCollectiveSummarySchema(
        publication_ids=publication_ids,
        summary=collective_summary_response.summary,
        keywords=collective_summary_response.keywords
    )

    return PublicationsCollectiveSummarySchema.model_validate(collective_summary)
