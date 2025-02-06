from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from enums.enums import ScenarioType, LevelType, DecisionType
from models import SDGLabelDecision, SDGPrediction, SDGLabelSummary, SDGLabelHistory
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.publications.publication import Publication
from schemas import SDGLabelDecisionSchemaFull
from settings.settings import SDGSLabelDecisionsRouterSettings
from utils.logger import logger

# Setup Logging
sdg_label_decisions_router_settings = SDGSLabelDecisionsRouterSettings()
logging = logger(sdg_label_decisions_router_settings.SDGLABELDECISIONS_ROUTER_LOG_NAME)

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
    prefix="/label-decisions",
    tags=["Label Decisions"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/{level}/",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve the newest SDG Label Decisions corresponding to the publications selected by dimensionality reduction."
)
async def get_newest_sdg_label_decisions_for_reduction(
    sdg: int,
    reduction_shorthand: str,
    level: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    try:
        user = verify_token(token, db)

        level_type = {1: LevelType.LEVEL_1, 2: LevelType.LEVEL_2, 3: LevelType.LEVEL_3}.get(level)
        if not level_type:
            raise HTTPException(status_code=400, detail="Invalid level. Must be 1, 2, or 3.")

        min_value, max_value = level_type.min_value, level_type.max_value

        publications = (
            db.query(Publication)
            .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
            .join(DimensionalityReduction, Publication.publication_id == DimensionalityReduction.publication_id)
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                getattr(SDGPrediction, f"sdg{sdg}").between(min_value, max_value),
                SDGPrediction.prediction_model == "Aurora"
            )
            .order_by(Publication.publication_id)
            .all()
        )

        publication_ids = [pub.publication_id for pub in publications]

        decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelSummary, SDGLabelDecision.history_id == SDGLabelSummary.history_id)
            .filter(SDGLabelSummary.publication_id.in_(publication_ids),
                    SDGLabelDecision.decided_label == 0)
            .all()
        )

        logging.info(f"Retrieved {len(decisions)} newest SDGLabelDecisions for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in decisions]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching newest SDGLabelDecisions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching newest SDGLabelDecisions: {e}")


@router.get(
    "/publications/{publication_id}",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve all SDGLabelDecision entries associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decisions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve all SDGLabelDecision entries for a publication's SDGLabelHistory.
    If no history exists, it will be initialized.
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

        # Get SDGLabelSummary (we know every publication has one)
        sdg_label_summary = publication.sdg_label_summary

        # Check if SDGLabelHistory exists
        history = db.query(SDGLabelHistory).filter(
            SDGLabelHistory.history_id == sdg_label_summary.history_id
        ).first()

        # If no history exists, create a new one
        if not history:
            logging.info(f"No SDGLabelHistory found for publication {publication_id}, creating a new history.")

            new_history = SDGLabelHistory(active=True)
            db.add(new_history)
            db.flush()  # Flush to get the new history_id

            # Link the SDGLabelSummary to the new history
            sdg_label_summary.history_id = new_history.history_id
            db.commit()
            db.refresh(new_history)

            history = new_history  # Assign the newly created history
            logging.info(f"Created new SDGLabelHistory (ID: {history.history_id}) for publication {publication_id}.")

        # If TODO: decisions exists, return the first newest one

        # Check for existing decisions
        if not history.decisions:
            logging.info(f"No SDGLabelDecisions found for publication {publication_id}, creating a new decision.")

            # Fetch the best SDG prediction from the 'Aurora' model
            prediction = (
                db.query(SDGPrediction)
                .filter(SDGPrediction.publication_id == publication_id, SDGPrediction.prediction_model == "Aurora")
                .first()
            )

            suggested_label: int = 0  # Default if no prediction is found

            if prediction:
                highest_sdg_key, highest_sdg_number, highest_sdg_value = prediction.get_highest_sdg()
                logging.info(
                    f"Highest SDG prediction: {highest_sdg_key} ({highest_sdg_number}), Value: {highest_sdg_value}."
                )
                suggested_label = highest_sdg_number  # Use extracted integer SDG number

            # Create a new SDGLabelDecision
            new_decision = SDGLabelDecision(
                history_id=history.history_id,
                publication_id=publication_id,
                suggested_label=suggested_label,
                decided_label=0,  # Default: not decided
                decision_type=DecisionType.CONSENSUS_MAJORITY,
                scenario_type=ScenarioType.NOT_ENOUGH_VOTES,
                expert_id=None,
                comment=None,
            )
            db.add(new_decision)
            db.commit()
            db.refresh(new_decision)

            logging.info(f"Created new SDGLabelDecision for publication {publication_id}.")
            return [SDGLabelDecisionSchemaFull.model_validate(new_decision)]

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in history.decisions]

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecisions for the publication",
        )



@router.get(
    "/publications/{publication_id}/{decision_id}",
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
    "/scenarios/{scenario}",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve all SDGLabelDecision entries associated with a specific scenario"
)
async def get_sdg_label_decisions_by_scenario(
    scenario: ScenarioType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve all SDGLabelDecision entries for a specific scenario.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for all SDGLabelDecisions with the specified scenario
        decisions = db.query(SDGLabelDecision).filter(SDGLabelDecision.scenario_type == scenario).all()

        if not decisions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelDecision entries found for scenario {scenario.value}",
            )

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in decisions]

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for scenario {scenario.value}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecisions for the scenario",
        )
