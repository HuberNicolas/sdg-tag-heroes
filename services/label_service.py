from sqlalchemy.orm import Session

from enums.enums import ScenarioType
from models import SDGUserLabel
from request_models.sdg_user_label import UserLabelRequest
from services.decision_service import DecisionService
from settings.settings import TimeZoneSettings, LabelServiceSettings
from utils.logger import logger

time_zone_settings = TimeZoneSettings()
label_service_settings = LabelServiceSettings()

# Setup Logging
logging = logger(label_service_settings.LABEL_SERVICE_LOG_NAME)


class LabelService:
    def __init__(self, db: Session):
        self.db = db
        logging.info("LabelService initialized.")

    def create_or_link_label(self, request: UserLabelRequest) -> SDGUserLabel:
        """
        Create or link an SDGUserLabel.
        """
        logging.info("Creating or linking a label.")
        decision_service = DecisionService(self.db)
        decision = decision_service.find_or_create_decision(request)

        new_user_label = SDGUserLabel(
            user_id=request.user_id,
            voted_label=request.voted_label,
            abstract_section=request.abstract_section or "",
            comment=request.comment or "",
        )
        self.db.add(new_user_label)
        self.db.flush()
        logging.info("Created a new user label.")

        decision.user_labels.append(new_user_label)
        decision_service.calculate_consensus(decision)

        scenario = decision_service.evaluate_vote_scenario(decision.user_labels)
        logging.info(f"Evaluated scenario: {scenario}.")

        """      
        if scenario == ScenarioType.CONFIRM:
            logging.info("Handling manual confirmation for CONFIRM scenario.")
            decision_service.handle_manual_confirmation(decision, request.user_id, request.voted_label)
        """


        self.db.commit()
        self.db.refresh(new_user_label)
        logging.info("Label creation/linking completed.")
        return new_user_label
