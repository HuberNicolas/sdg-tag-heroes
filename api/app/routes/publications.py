import time
from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery, SimilarityQueryRequest
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import SDGPrediction, SDGLabelDecision, Fact, Summary
from models.publications.author import Author
# Import models
from models.publications.publication import Publication
from models.request import PublicationIdsRequest

from schemas.dimensionality_reduction import DimensionalityReductionSchemaBase, DimensionalityReductionSchemaFull
from schemas.publications.author import AuthorSchemaBase, AuthorSchemaFull
from schemas.publications.publication import PublicationSchemaBase, PublicationSchemaFull
from schemas.sdg_label_decision import SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull
from schemas.sdg_label_history import SDGLabelHistorySchemaFull
from schemas.sdg_label_summary import SDGLabelSummarySchemaFull
from schemas.sdg_prediction import SDGPredictionSchemaFull, SDGPredictionSchemaBase
from schemas.sdg_user_label import SDGUserLabelSchemaFull, SDGUserLabelSchemaBase

from services.gpt_explainer import SDGExplainer, SummarizePublicationStrategy, CollectiveSummaryResponse
from services.similarity_query import SimilarityQuery

from settings.settings import PublicationsRouterSettings
publications_router_settings = PublicationsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(publications_router_settings.PUBLICATIONS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/publications",
    tags=["publications"],
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

@router.get(
    "/sdg_label_decisions/{decision_id}/sdg_user_labels",
    response_model=List[SDGUserLabelSchemaBase],
    description="Retrieve all SDGUserLabel entries associated with a specific SDGLabelDecision"
)
async def get_sdg_user_labels(
    decision_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGUserLabelSchemaBase]:
    """
    Retrieve all SDGUserLabel entries for a specific SDGLabelDecision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelDecision
        decision = db.query(SDGLabelDecision).filter(SDGLabelDecision.decision_id == decision_id).first()

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found",
            )

        # Return the list of SDGUserLabels associated with the decision
        return [SDGUserLabelSchemaBase.model_validate(label) for label in decision.user_labels]

    except Exception as e:
        logging.error(f"Error fetching SDGUserLabels for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGUserLabels for the decision",
        )

@router.get(
    "/sdg_label_decisions/{decision_id}/sdg_user_labels/{label_id}",
    response_model=SDGUserLabelSchemaFull,
    description="Retrieve a specific SDGUserLabel entry associated with a specific SDGLabelDecision"
)
async def get_sdg_user_label(
    decision_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGUserLabelSchemaFull:
    """
    Retrieve a specific SDGUserLabel entry for a specific SDGLabelDecision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelDecision
        decision = db.query(SDGLabelDecision).filter(SDGLabelDecision.decision_id == decision_id).first()

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found",
            )

        # Check if the SDGUserLabel is associated with the decision
        label = next((l for l in decision.user_labels if l.label_id == label_id), None)

        if not label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGUserLabel with ID {label_id} not associated with decision ID {decision_id}",
            )

        return SDGUserLabelSchemaFull.model_validate(label)

    except Exception as e:
        logging.error(f"Error fetching SDGUserLabel ID {label_id} for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGUserLabel for the decision",
        )


@router.get(
    "/{publication_id}/sdg_label_history",
    response_model=SDGLabelHistorySchemaFull,
    description="Retrieve the SDGLabelHistory associated with a specific publication"
)
async def get_sdg_label_history(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelHistorySchemaFull:
    """
    Retrieve the SDGLabelHistory for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelHistory
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        history = publication.sdg_label_summary.history

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        return SDGLabelHistorySchemaFull.model_validate(history)

    except Exception as e:
        logging.error(f"Error fetching SDGLabelHistory for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelHistory for the publication",
        )

@router.get(
    "/{publication_id}/sdg_label_summary",
    response_model=SDGLabelSummarySchemaFull,
    description="Retrieve the SDGLabelSummary associated with a specific publication"
)
async def get_sdg_label_summary(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelSummarySchemaFull:
    """
    Retrieve the SDGLabelSummary for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelSummary
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelSummary found for publication ID {publication_id}",
            )

        return SDGLabelSummarySchemaFull.model_validate(publication.sdg_label_summary)

    except Exception as e:
        logging.error(f"Error fetching SDGLabelSummary for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelSummary for the publication",
        )

@router.get(
    "/{publication_id}/sdg_label_history/decisions",
    response_model=List[SDGLabelDecisionSchemaBase],
    description="Retrieve all SDGLabelDecision entries associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decisions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaBase]:
    """
    Retrieve all SDGLabelDecision entries for a publication's SDGLabelHistory.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelHistory
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        history = publication.sdg_label_summary.history

        if not history or not history.decisions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelDecision entries found for publication ID {publication_id}",
            )

        return [SDGLabelDecisionSchemaBase.model_validate(decision) for decision in history.decisions]

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecisions for the publication",
        )


@router.get(
    "/{publication_id}/sdg_label_history/decisions/{decision_id}",
    response_model=SDGLabelDecisionSchemaFull,
    description="Retrieve a specific SDGLabelDecision entry associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decision(
    publication_id: int,
    decision_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelDecisionSchemaFull:
    """
    Retrieve a specific SDGLabelDecision entry for a publication's SDGLabelHistory.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelHistory
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        history = publication.sdg_label_summary.history

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        decision = next((d for d in history.decisions if d.decision_id == decision_id), None)

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found for publication ID {publication_id}",
            )

        return SDGLabelDecisionSchemaFull.model_validate(decision)

    except Exception as e:
        logging.error(
            f"Error fetching SDGLabelDecision ID {decision_id} for publication ID {publication_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecision for the publication",
        )


@router.get(
    "/{publication_id}/sdg_predictions",
    response_model=List[SDGPredictionSchemaBase],
    description="Retrieve all SDG predictions associated with a specific publication"
)
async def get_sdg_predictions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGPredictionSchemaBase]:
    """
    Retrieve all SDG predictions for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDG predictions
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Return the list of SDG predictions associated with the publication
        return [
            SDGPredictionSchemaBase.model_validate(prediction)
            for prediction in publication.sdg_predictions
        ]

    except Exception as e:
        logging.error(f"Error fetching SDG predictions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG predictions for the publication",
        )

@router.get(
    "/{publication_id}/sdg_predictions/{prediction_id}",
    response_model=SDGPredictionSchemaFull,
    description="Retrieve a specific SDG prediction associated with a specific publication"
)
async def get_sdg_prediction(
    publication_id: int,
    prediction_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGPredictionSchemaFull:
    """
    Retrieve a specific SDG prediction for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Check if the SDG prediction is associated with the publication
        sdg_prediction = next(
            (prediction for prediction in publication.sdg_predictions if prediction.prediction_id == prediction_id),
            None,
        )

        if not sdg_prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG prediction with ID {prediction_id} not associated with publication ID {publication_id}",
            )

        # Return the detailed information of the specific SDG prediction
        return SDGPredictionSchemaFull.model_validate(sdg_prediction)

    except Exception as e:
        logging.error(
            f"Error fetching SDG prediction ID {prediction_id} for publication ID {publication_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDG prediction for the publication",
        )


@router.get(
    "/{publication_id}/dimensionality_reductions",
    response_model=List[DimensionalityReductionSchemaBase],
    description="Retrieve all dimensionality reductions associated with a specific publication"
)
async def get_dimensionality_reductions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[DimensionalityReductionSchemaBase]:
    """
    Retrieve all dimensionality reductions for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its dimensionality reductions
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Return the list of dimensionality reductions associated with the publication
        return [
            DimensionalityReductionSchemaBase.model_validate(dim_red)
            for dim_red in publication.dimensionality_reductions
        ]

    except Exception as e:
        logging.error(f"Error fetching dimensionality reductions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching dimensionality reductions for the publication",
        )

@router.get(
    "/{publication_id}/dimensionality_reductions/{dim_red_id}",
    response_model=DimensionalityReductionSchemaFull,
    description="Retrieve a specific dimensionality reduction associated with a specific publication"
)
async def get_dimensionality_reduction(
    publication_id: int,
    dim_red_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> DimensionalityReductionSchemaFull:
    """
    Retrieve a specific dimensionality reduction for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Check if the dimensionality reduction is associated with the publication
        dim_reduction = next(
            (dim_red for dim_red in publication.dimensionality_reductions if dim_red.dim_red_id == dim_red_id), None
        )

        if not dim_reduction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dimensionality reduction with ID {dim_red_id} not associated with publication ID {publication_id}",
            )

        # Return the detailed information of the specific dimensionality reduction
        return DimensionalityReductionSchemaFull.model_validate(dim_reduction)

    except Exception as e:
        logging.error(
            f"Error fetching dimensionality reduction ID {dim_red_id} for publication ID {publication_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the dimensionality reduction for the publication",
        )


@router.get(
    "/{publication_id}/authors/{author_id}",
    response_model=AuthorSchemaFull,
    description="Retrieve a specific author associated with a specific publication"
)
async def get_publication_author(
    publication_id: int,
    author_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AuthorSchemaFull:
    """
    Retrieve a specific author for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Check if the author is associated with the publication
        author = next((author for author in publication.authors if author.author_id == author_id), None)

        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not associated with publication ID {publication_id}",
            )

        # Return the detailed information of the specific author
        return AuthorSchemaFull.model_validate(author)

    except Exception as e:
        logging.error(f"Error fetching author ID {author_id} for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the author for the publication",
        )


@router.get(
    "/{publication_id}/authors",
    response_model=List[AuthorSchemaBase],
    description="Retrieve all authors associated with a specific publication"
)
async def get_publication_authors(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[AuthorSchemaBase]:
    """
    Retrieve all authors for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its authors
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Return the list of authors associated with the publication
        return [AuthorSchemaBase.model_validate(author) for author in publication.authors]

    except Exception as e:
        logging.error(f"Error fetching authors for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors for the publication",
        )

@router.get(
    "/by-sdg-values",
    response_model=Dict[str, Any],  # Returns both statistics and publication data
    description=(
        "Retrieve publications filtered by SDG values within a specified range. "
        "You can specify a fixed model when multiple models are available."
    ),
)
async def get_publications_by_sdg_values(
    sdg_range: Tuple[float, float] = Query(..., description="Range for SDG values, e.g., (0.98, 0.99)"),
    limit: int = Query(10, description="Limit for the number of publications per SDG group"),
    sdgs: Optional[List[int]] = Query(None, description="List of specific SDGs to filter, e.g., [1, 3, 12]"),
    model: Optional[str] = Query(None, description="Fixed model name to filter by, e.g., 'model_A'"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Retrieve publications filtered by SDG values within a specified range.
    Always returns the full model with all related data included.
    """
    # Verify the token before proceeding
    user = verify_token(token, db)  # Raises HTTPException if the token is invalid or expired

    # Unpack the range
    min_value, max_value = sdg_range

    print(f"Raw SDGs Query Param: {sdgs}")

    # Check if `sdgs` is provided and not empty; otherwise, use the default range
    if sdgs is not None and len(sdgs) > 0:
        sdg_list = sdgs
    else:
        sdg_list = list(range(1, 18))

    # Result dictionary to store publications and statistics
    result = {
        "statistics": {
            "general_range": {"min_value": min_value, "max_value": max_value},
            "sdg_statistics": {}
        },
        "publications": {}
    }

    for sdg in sdg_list:
        # Construct the base query for the SDG, joining with SDGPrediction
        query = db.query(Publication).join(SDGPrediction)

        # Filter the SDGPrediction objects
        sdg_attr = f"sdg{sdg}"
        if model:
            # If a model is specified, filter by model and SDG value range
            query = query.filter(
                SDGPrediction.prediction_model == model,
                getattr(SDGPrediction, sdg_attr).between(min_value, max_value)
            )
        else:
            # No model specified: Filter by SDG value range
            query = query.filter(getattr(SDGPrediction, sdg_attr).between(min_value, max_value))

        # Order the query by the SDG value in descending order and limit the results
        query = query.order_by(getattr(SDGPrediction, sdg_attr).desc()).limit(limit)

        # Fetch publications
        publications = query.all()

        # Collect statistics
        retrieved_count = len(publications)
        min_pred = float('inf')
        max_pred = float('-inf')
        model_counts = defaultdict(int)

        # Convert each publication to the full Pydantic model and update statistics
        full_publications = []
        for publication in publications:
            for prediction in publication.sdg_predictions:
                if model and prediction.prediction_model != model:
                    continue
                pred_value = getattr(prediction, sdg_attr)
                min_pred = min(min_pred, pred_value)
                max_pred = max(max_pred, pred_value)
                model_counts[prediction.prediction_model] += 1

            # Add the full publication model
            full_publications.append(PublicationSchemaFull.model_validate(publication))

        # Prepare SDG-specific statistics
        result["statistics"]["sdg_statistics"][f"sdg{sdg}"] = {
            "limit": limit,
            "retrieved_count": retrieved_count,
            "min_pred": min_pred if min_pred != float('inf') else None,
            "max_pred": max_pred if max_pred != float('-inf') else None,
            "pubs_per_model": dict(model_counts)
        }

        # Add publications to result
        result["publications"][f"sdg{sdg}"] = full_publications

    return result

@router.post(
    "/",
    response_model=List[PublicationSchemaFull],
    description="Get a list of publications by IDs"
)
async def get_publications_by_ids(
    request: PublicationIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[PublicationSchemaFull]:
    user = verify_token(token, db)  # Ensure user is authenticated
    publication_ids = request.publication_ids  # Access the list of IDs
    publications = db.query(Publication).filter(Publication.publication_id.in_(publication_ids)).all()
    return [PublicationSchemaFull.model_validate(pub) for pub in publications]

@router.get(
    "/",
    response_model=Page[Union[PublicationSchemaFull]],
    description="Get all publications"
)
async def get_publications(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Page[PublicationSchemaFull]:
    """
    Retrieve all publications with optional minimal or full details based on the 'minimal' query parameter.
    Supports pagination.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        # Base query for fetching publications
        query = db.query(Publication)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_paginate(query)

        paginated_query.items = [PublicationSchemaFull.model_validate(pub) for pub in paginated_query.items]

        return paginated_query

    except Exception as e:
        logging.error(f"Error fetching publications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching publications",
        )

@router.get(
    "/{publication_id}",
    response_model=PublicationSchemaFull,
    description="Get a single publication by ID"
)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> PublicationSchemaFull:
    """
    Retrieve a single publication by ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query to fetch the publication by ID
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        # If not found, raise 404 error
        if not publication:
            logging.warning(f"Publication with ID {publication_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found"
            )

        # Validate and return the full schema
        return PublicationSchemaFull.model_validate(publication)

    except Exception as e:
        logging.error(f"Error fetching publication with ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the publication",
        )


@router.get("/{publication_id}/explain/goal/{sdg_id}", response_model=dict,
            description="Explain the relevance of a publication to a specific SDG")
async def explain_publication_sdg_relevance(publication_id: int, sdg_id: int, db: Session = Depends(get_db),
                                            token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token, db)  # Ensure user is authenticated
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Here you would integrate with your SDG explanation service
    explanation = SDGExplainer().explain(publication, goal=str(sdg_id))

    return {"publication_id": publication_id, "sdg_id": sdg_id, "explanation": explanation}


@router.get("/{publication_id}/explain/target/{target_id}", response_model=dict,
            description="Explain the relevance of a publication to a specific SDG target")
async def explain_publication_sdg_target(publication_id: int, target_id: str, db: Session = Depends(get_db),
                                         token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token, db)  # Ensure user is authenticated
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    target_explanation = SDGExplainer().explain(publication,
                                                target=target_id)

    return {"publication_id": publication_id, "target_id": target_id, "explanation": target_explanation}

@router.get("/{publication_id}/keywords", response_model=dict, description="Extract keywords from a publication")
async def extract_keywords(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Extract keywords from a specific publication using the GPT-based explainer.
    """
    # Verify the user's token
    user = verify_token(token, db)  # Ensure user is authenticated

    # Fetch the publication by its ID
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Ensure the publication has content for keyword extraction
    if not publication.title and not publication.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No content available for keyword extraction")

    # Combine title and description for the GPT explainer
    title = publication.title or ""
    abstract = publication.description or ""

    try:
        # Use the GPT-based keyword extractor
        keywords = SDGExplainer().extract_keywords(title, abstract)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Keyword extraction failed: {str(e)}")

    # Return the extracted keywords
    return {"publication_id": publication_id, "keywords": keywords}



@router.get("/{publication_id}/facts", response_model=dict, description="Generate a 'Did-You-Know' fact from a scientific abstract")
async def create_did_you_know_fact(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Generate a 'Did-You-Know' fact based on the given title and abstract.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    # Fetch the publication by its ID
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Check if a fact already exists in the database
    existing_fact = db.query(Fact).filter(Fact.publication_id == publication_id).first()
    if existing_fact:
        return {"publication_id": publication_id, "fact": existing_fact.content}

    # Ensure the publication has content for fact generation
    if not publication.title and not publication.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No content available for fact generation")

    # Combine title and description for the GPT explainer
    title = publication.title or ""
    abstract = publication.description or ""

    # Use the SDGExplainer to generate the fact
    try:
        new_fact_content = SDGExplainer().create_fact(title=title, abstract=abstract)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fact generation failed: {str(e)}")

    # Save the new fact to the database
    new_fact = Fact(
        content=new_fact_content,
        publication_id=publication_id
    )
    db.add(new_fact)
    db.commit()
    db.refresh(new_fact)

    # Return the generated fact
    return {"publication_id": publication_id, "fact": new_fact_content}

@router.get("/{publication_id}/summary", response_model=dict, description="Generate or retrieve a summary for a publication.")
async def create_or_get_publication_summary(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Generate a concise summary for a publication if it doesn't exist, or fetch the existing summary.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    # Fetch the publication by its ID
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Check if a summary already exists in the database
    existing_summary = db.query(Summary).filter(Summary.publication_id == publication_id).first()
    if existing_summary:
        return {"publication_id": publication_id, "summary": existing_summary.content}

    # Ensure the publication has content for summary generation
    if not publication.title and not publication.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content available for summary generation"
        )

    # Combine title and description for summary generation
    title = publication.title or ""
    abstract = publication.description or ""

    # Use the SummarizePublicationStrategy to generate the summary
    try:
        new_summary_content = SDGExplainer().summarize_publication(title=title, abstract=abstract)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Summary generation failed: {str(e)}")

    # Save the new summary to the database
    new_summary = Summary(
        content=new_summary_content,
        publication_id=publication_id
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    # Return the generated summary
    return {"publication_id": publication_id, "summary": new_summary_content}


@router.post(
    "/similar/{top_k}",
    response_model=dict,
    description="Retrieve publications similar to the user query along with their similarity scores."
)
async def get_similar_publications(
    top_k: int,
    request: SimilarityQueryRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Retrieve publications similar to the user query based on vector similarity.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    # Initialize the similarity service
    similarity_service = SimilarityQuery(qdrant_client)

    # Generate the query vector
    start = time.time()
    query_vector = similarity_service.generate_user_query_vector(request.user_query)
    end = time.time()
    query_building_time = end - start

    start = time.time()
    # Perform the similarity search
    search_results = similarity_service.search_publications(
        query_vector=query_vector,
        collection_name="publications-mt",
        top_k=top_k
    )
    end = time.time()
    search_time = end - start

    # Extract publication IDs and similarity scores
    publication_scores = {result.payload["sql_id"]: result.score for result in search_results}
    publication_ids = list(publication_scores.keys())

    # Fetch publication details from the database
    publications = (
        db.query(Publication)
        .filter(Publication.publication_id.in_(publication_ids))
        .all()
    )

    # Build the response
    results = [
        {
            **PublicationSchemaFull.model_validate(pub).dict(),  # Validate and convert to dict
            "score": publication_scores.get(pub.publication_id, 0.0)  # Add similarity score
        }
        for pub in publications
    ]

    # Return the response
    return {
        "query_building_time": query_building_time,
        "search_time": search_time,
        "user_query": request.user_query,
        "results": sorted(results, key=lambda x: x["score"], reverse=True)
    }

@router.post(
    "/summaries",
    response_model=CollectiveSummaryResponse,
    description="Generate a single cohesive summary and keywords for a set of publications by IDs."
)
async def create_collective_summary(
    request: PublicationIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> CollectiveSummaryResponse:
    """
    Generate a single cohesive summary and keywords for a set of publications by their IDs.
    """
    user = verify_token(token, db)  # Ensure user is authenticated
    publication_ids = request.publication_ids  # Access the list of IDs

    # Fetch the publications from the database
    publications = db.query(Publication).filter(Publication.publication_id.in_(publication_ids)).all()

    if not publications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No publications found for the given IDs.")

    # Prepare data for summarization
    publication_data = [
        {"id": pub.publication_id, "title": pub.title or "", "abstract": pub.description or ""}
        for pub in publications
    ]

    # Use SDGExplainer to generate a collective summary and keywords
    try:
        result = SDGExplainer().summarize_publications(publications=publication_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Summary generation failed: {str(e)}")

    return result


