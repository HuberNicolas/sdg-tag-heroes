from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from enums.enums import ScenarioType, LevelType, DecisionType
from models import SDGLabelDecision, SDGPrediction, SDGLabelSummary, SDGLabelHistory, Annotation, SDGUserLabel
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.publications.publication import Publication
from schemas import SDGLabelDecisionSchemaFull, SDGLabelDecisionSchemaExtended
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
    "/global/scenarios/least-labeled/{top_k}",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve SDG Label Decisions for the top-k publications associated with the least-labeled SDG. If no decision exists, create a new one."
)
async def get_or_create_least_labeled_sdg_decisions(
    top_k: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Identify the SDG with the least number of labeled instances, retrieve SDGLabelDecisions
    for the top-k publications associated with it, and if a publication has no decision, create a new one.
    Excludes decisions with scenario_type == ScenarioType.DECIDED.
    """
    try:
        user = verify_token(token, db)

        # Count occurrences of SDG labels in SDGLabelSummary
        sdg_counts = (
            db.query(
                *[func.sum(getattr(SDGLabelSummary, f"sdg{i}")).label(f"sdg{i}") for i in range(1, 18)]
            )
            .first()
        )

        # Find the SDG with the least labels
        least_labeled_sdg = min(
            (i for i in range(1, 18) if getattr(sdg_counts, f"sdg{i}") is not None),
            key=lambda i: getattr(sdg_counts, f"sdg{i}"),
        )

        logging.info(f"Least labeled SDG is SDG{least_labeled_sdg}.")

        # Fetch the top-k publications related to the least labeled SDG
        publications = (
            db.query(Publication)
            .join(SDGLabelSummary, Publication.publication_id == SDGLabelSummary.publication_id)
            .filter(
                getattr(SDGLabelSummary, f"sdg{least_labeled_sdg}") == 1  # Filter by least labeled SDG
            )
            .limit(top_k)  # Limit to top-k publications
            .all()
        )

        decisions_list = []

        for publication in publications:
            sdg_label_summary = publication.sdg_label_summary

            # Check if SDGLabelHistory exists
            history = db.query(SDGLabelHistory).filter(
                SDGLabelHistory.history_id == sdg_label_summary.history_id
            ).first()

            # If no history exists, create a new one
            if not history:
                logging.info(f"No SDGLabelHistory found for publication {publication.publication_id}, creating a new history.")

                new_history = SDGLabelHistory(active=True)
                db.add(new_history)
                db.flush()  # Flush to get the new history_id

                # Link the SDGLabelSummary to the new history
                sdg_label_summary.history_id = new_history.history_id
                db.commit()
                db.refresh(new_history)

                history = new_history  # Assign the newly created history
                logging.info(f"Created new SDGLabelHistory (ID: {history.history_id}) for publication {publication.publication_id}.")

            # Filter out decisions that have scenario_type == DECIDED
            existing_decisions = [
                decision for decision in history.decisions if decision.scenario_type != ScenarioType.DECIDED
            ]

            if not existing_decisions:
                logging.info(f"No valid SDGLabelDecisions found for publication {publication.publication_id}, creating a new decision.")

                # Fetch the best SDG prediction from the 'Aurora' model
                prediction = (
                    db.query(SDGPrediction)
                    .filter(SDGPrediction.publication_id == publication.publication_id, SDGPrediction.prediction_model == "Aurora")
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
                    publication_id=publication.publication_id,
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

                logging.info(f"Created new SDGLabelDecision for publication {publication.publication_id}.")
                decisions_list.append(SDGLabelDecisionSchemaFull.model_validate(new_decision))
            else:
                decisions_list.extend([SDGLabelDecisionSchemaFull.model_validate(decision) for decision in existing_decisions])

        return decisions_list

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for the least-labeled SDG: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDGLabelDecisions: {e}")

@router.get(
    "/global/scenarios/max-entropy/{top_k}",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve SDG Label Decisions for the top-k SDGs with the highest entropy. If no decision exists, create a new one."
)
async def get_or_create_top_k_entropy_sdg_decisions(
    top_k: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Identify the top-k SDGs with the highest entropy, retrieve their SDGLabelDecisions,
    and if a publication has no decision, create a new one.
    """
    try:
        user = verify_token(token, db)

        # Find the top-k SDGs with the highest entropy
        top_entropy_sdgs = (
            db.query(SDGPrediction)
            .order_by(SDGPrediction.entropy.desc())
            .filter(
                SDGPrediction.prediction_model == "Aurora",
            )
            .limit(top_k)
            .all()
        )

        if not top_entropy_sdgs:
            raise HTTPException(status_code=404, detail="No SDG predictions found.")

        decisions_list = []

        for max_entropy_sdg in top_entropy_sdgs:
            publication_id = max_entropy_sdg.publication_id
            logging.info(f"Processing SDG with highest entropy for publication {publication_id}.")

            # Fetch the corresponding publication
            publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

            if not publication:
                raise HTTPException(status_code=404, detail=f"Publication with ID {publication_id} not found.")

            sdg_label_summary = publication.sdg_label_summary

            # Check if SDGLabelHistory exists
            history = db.query(SDGLabelHistory).filter(
                SDGLabelHistory.history_id == sdg_label_summary.history_id
            ).first()

            # If no history exists, create a new one
            if not history:
                logging.info(f"No SDGLabelHistory found for publication {publication.publication_id}, creating a new history.")

                new_history = SDGLabelHistory(active=True)
                db.add(new_history)
                db.flush()  # Flush to get the new history_id

                # Link the SDGLabelSummary to the new history
                sdg_label_summary.history_id = new_history.history_id
                db.commit()
                db.refresh(new_history)

                history = new_history  # Assign the newly created history
                logging.info(f"Created new SDGLabelHistory (ID: {history.history_id}) for publication {publication.publication_id}.")

            # Check for existing decisions
            if not history.decisions:
                logging.info(f"No SDGLabelDecisions found for publication {publication.publication_id}, creating a new decision.")

                # Fetch the best SDG prediction from the 'Aurora' model
                prediction = (
                    db.query(SDGPrediction)
                    .filter(SDGPrediction.publication_id == publication.publication_id, SDGPrediction.prediction_model == "Aurora")
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
                    publication_id=publication.publication_id,
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

                logging.info(f"Created new SDGLabelDecision for publication {publication.publication_id}.")
                decisions_list.append(SDGLabelDecisionSchemaFull.model_validate(new_decision))
            else:
                decisions_list.extend([SDGLabelDecisionSchemaFull.model_validate(decision) for decision in history.decisions])

        return decisions_list

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching top-{top_k} max-entropy SDGLabelDecisions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDGLabelDecisions: {e}")



@router.get(
    "/{reduction_shorthand}/scenarios/{scenario_type}/",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve SDG Label Decisions for a given reduction shorthand, and scenario type."
)
async def get_sdg_label_decisions_for_scenario(
    reduction_shorthand: str,
    scenario_type: ScenarioType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve SDG Label Decisions for a specific reduction shorthand and scenario type.
    """
    try:
        user = verify_token(token, db)

        decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelSummary, SDGLabelDecision.history_id == SDGLabelSummary.history_id)
            .join(Publication, SDGLabelSummary.publication_id == Publication.publication_id)
            .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                SDGPrediction.prediction_model == "Aurora",
                SDGLabelDecision.scenario_type == scenario_type  # Filter by scenario type
            )
            .order_by(Publication.publication_id)
            .all()
        )

        logging.info(f"Retrieved {len(decisions)} SDGLabelDecisions for scenario type '{scenario_type}' and reduction shorthand '{reduction_shorthand}'.")

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in decisions]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDGLabelDecisions: {e}")

@router.get(
    "/sdgs/{sdg}/{reduction_shorthand}/scenarios/{scenario_type}/",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve SDG Label Decisions for a given SDG, reduction shorthand, and scenario type."
)
async def get_sdg_label_decisions_for_scenario(
    sdg: int,
    reduction_shorthand: str,
    scenario_type: ScenarioType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve SDG Label Decisions for a specific SDG, reduction shorthand, and scenario type.
    """
    try:
        user = verify_token(token, db)

        decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelSummary, SDGLabelDecision.history_id == SDGLabelSummary.history_id)
            .join(Publication, SDGLabelSummary.publication_id == Publication.publication_id)
            .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
            .join(DimensionalityReduction, Publication.publication_id == DimensionalityReduction.publication_id)
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                DimensionalityReduction.sdg == sdg,
                SDGPrediction.prediction_model == "Aurora",
                SDGLabelDecision.scenario_type == scenario_type  # Filter by scenario type
            )
            .order_by(Publication.publication_id)
            .all()
        )

        logging.info(f"Retrieved {len(decisions)} SDGLabelDecisions for SDG {sdg}, scenario type '{scenario_type}', and reduction shorthand '{reduction_shorthand}'.")

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in decisions]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDGLabelDecisions: {e}")


@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/{level}/",
    response_model=List[SDGLabelDecisionSchemaExtended],
    description="Retrieve the newest SDG Label Decisions corresponding to the publications selected by dimensionality reduction."
)
async def get_newest_sdg_label_decisions_for_reduction(
    sdg: int,
    reduction_shorthand: str,
    level: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaExtended]:
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
            .filter(
                SDGLabelSummary.publication_id.in_(publication_ids),
                SDGLabelDecision.decided_label == 0
            )
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        logging.info(f"Retrieved {len(decisions)} newest SDGLabelDecisions for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")

        return [SDGLabelDecisionSchemaExtended.model_validate(decision) for decision in decisions]
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


@router.get(
    "/{reduction_shorthand}/{part_number}/{total_parts}/",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve or initialize SDGLabelDecision entries for a batch of publications linked to a specific part of dimensionality reductions."
)
async def get_sdg_label_decisions_partitioned(
    reduction_shorthand: str,
    part_number: int,
    total_parts: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve or initialize SDGLabelDecision entries for a batch of publications linked to a specific part of dimensionality reductions.
    If no decisions exist, they will be created based on SDG predictions.
    """
    try:
        # Ensure user is authenticated
        user = verify_token(token, db)

        # Validate part_number and total_parts
        if part_number < 1 or part_number > total_parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"part_number must be between 1 and {total_parts}",
            )

        # Query the total number of dimensionality reductions for the given shorthand
        total_count = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).count()

        logging.debug(f"Total Count (Dimensionality Reductions): {total_count}")

        if total_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No dimensionality reductions found for shorthand: {reduction_shorthand}",
            )

        # Calculate the start and end indices for the requested part
        part_size = total_count // total_parts
        remainder = total_count % total_parts

        start_index = (part_number - 1) * part_size
        end_index = start_index + part_size

        logging.debug(f"Part Size: {part_size}, Remainder: {remainder}, Start Index: {start_index}, End Index: {end_index}")

        # Adjust for the remainder in the last part
        if part_number == total_parts:
            end_index += remainder

        # Fetch the specific part of dimensionality reductions
        dimensionality_reductions = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).order_by(DimensionalityReduction.publication_id).offset(start_index).limit(end_index - start_index).all()

        logging.debug(f"Dimensionality Reductions Retrieved: {len(dimensionality_reductions)}")

        # Extract publication IDs
        publication_ids = [dim_red.publication_id for dim_red in dimensionality_reductions]

        if not publication_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No publications found for the specified part of dimensionality reductions.",
            )

        # Fetch all SDGLabelDecisions for these publications
        decisions = db.query(SDGLabelDecision).filter(
            SDGLabelDecision.publication_id.in_(publication_ids)
        ).all()

        existing_decision_pub_ids = {decision.publication_id for decision in decisions}
        missing_pub_ids = set(publication_ids) - existing_decision_pub_ids

        new_decisions = []

        # Create missing SDGLabelDecisions
        for publication_id in missing_pub_ids:
            publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
            if not publication:
                continue  # Skip if somehow publication doesn't exist

            # Retrieve the SDGLabelSummary
            sdg_label_summary = publication.sdg_label_summary
            if not sdg_label_summary:
                continue

            # Retrieve or create SDGLabelHistory
            history = db.query(SDGLabelHistory).filter(
                SDGLabelHistory.history_id == sdg_label_summary.history_id
            ).first()

            if not history:
                history = SDGLabelHistory(active=True)
                db.add(history)
                db.flush()  # Get history_id
                sdg_label_summary.history_id = history.history_id
                db.commit()
                db.refresh(history)

            # Fetch the best SDG prediction from 'Aurora' model
            prediction = db.query(SDGPrediction).filter(
                SDGPrediction.publication_id == publication_id,
                SDGPrediction.prediction_model == "Aurora"
            ).first()

            suggested_label = 0  # Default if no prediction exists
            if prediction:
                _, highest_sdg_number, _ = prediction.get_highest_sdg()
                suggested_label = highest_sdg_number  # Extracted integer SDG number

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
            new_decisions.append(new_decision)

        if new_decisions:
            db.commit()
            for decision in new_decisions:
                db.refresh(decision)

        # Combine and return all decisions
        all_decisions = decisions + new_decisions

        logging.info(f"Total SDGLabelDecisions returned: {len(all_decisions)}")
        return all_decisions

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGLabelDecisions.",
        )


@router.get(
    "/users/{user_id}",
    response_model=List[SDGLabelDecisionSchemaExtended],
    description="Retrieve all SDG label decisions a user has interacted with via SDGUserLabels, annotations, or direct decision creation."
)
async def get_user_interacted_sdg_label_decisions(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaExtended]:
    """
    Retrieve all SDGLabelDecisions a user has interacted with in any of the following ways:
    - They created the SDGLabelDecision.
    - They created an SDGUserLabel that is linked to a decision.
    - They created an Annotation directly linked to an SDGLabelDecision.
    - They created an Annotation linked to an SDGUserLabel that is associated with an SDGLabelDecision.

    The response includes:
    - All attached SDGUserLabels with their annotations.
    - All annotations directly linked to the SDGLabelDecision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Fetch all SDGLabelDecisions where the user is the creator (direct interaction)
        user_created_decisions = (
            db.query(SDGLabelDecision)
            .filter(SDGLabelDecision.expert_id == user_id)  # Assuming the expert_id is the creator
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Fetch all SDGLabelDecisions where the user has created an SDGUserLabel
        user_label_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.user_labels)
            .filter(SDGUserLabel.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Fetch all SDGLabelDecisions where the user has created an Annotation directly linked to the decision
        annotation_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.annotations)
            .filter(Annotation.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Fetch all SDGLabelDecisions where the user has created an Annotation linked to an SDGUserLabel associated with a decision
        annotation_user_label_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.user_labels)
            .join(SDGUserLabel.annotations)
            .filter(Annotation.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Combine results and remove duplicates
        all_decisions = list(set(
            user_created_decisions +
            user_label_decisions +
            annotation_decisions +
            annotation_user_label_decisions
        ))

        if not all_decisions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelDecisions found for user ID {user_id}",
            )

        return [SDGLabelDecisionSchemaExtended.model_validate(decision) for decision in all_decisions]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDGLabelDecisions for user {user_id}.",
        )
