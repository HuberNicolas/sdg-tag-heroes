from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy.orm import Session, sessionmaker
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from models import SDGLabelSummary

from schemas.sdg_label_summary import SDGLabelSummarySchemaFull, SDGLabelSummarySchemaBase


from settings.settings import SDGSLabelSummariesRouterSettings
sdg_label_summaries_settings = SDGSLabelSummariesRouterSettings()

from utils.logger import logger
logging = logger(sdg_label_summaries_settings.SDGLABELSUMMARIES_ROUTER_LOG_NAME)


router = APIRouter(
    prefix="/label-summaries",
    tags=["label-summaries"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

security = Security()
# OAuth2 scheme for token authentication
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


@router.get(
    "/",
    response_model=Page[SDGLabelSummarySchemaBase],
    description="Retrieve all SDGLabelSummaries",
)
async def get_label_summaries(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Page[SDGLabelSummarySchemaBase]:
    """
    Retrieve all SDGLabelSummary entries.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for all SDGLabelSummaries
        query = db.query(SDGLabelSummary)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_paginate(query)

        paginated_query.items = [SDGLabelSummarySchemaBase.model_validate(label_summary) for label_summary in paginated_query.items]


        return paginated_query

    except Exception as e:
        print(e)
        logging.error(f"Error fetching SDGLabelSummaries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGLabelSummaries",
        )


@router.get(
    "/{label_summary_id}",
    response_model=SDGLabelSummarySchemaFull,
    description="Retrieve a specific SDGLabelSummary by ID",
)
async def get_label_summary(
    label_summary_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelSummarySchemaFull:
    """
    Retrieve a specific SDGLabelSummary by its ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelSummary
        label_summary = db.query(SDGLabelSummary).filter(SDGLabelSummary.sdg_label_summary_id == label_summary_id).first()

        if not label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelSummary with ID {label_summary_id} not found",
            )

        return SDGLabelSummarySchemaFull.model_validate(label_summary)

    except Exception as e:
        logging.error(f"Error fetching SDGLabelSummary ID {label_summary_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelSummary",
        )
