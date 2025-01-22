from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from requests_models.user_profiles_gpt import UserProfileInterestsRequest, UserProfileSkillsRequest
from schemas.gpt_assistant.gpt_assistant import UserEnrichedInterestsDescriptionSchema, \
    UserEnrichedSkillsDescriptionSchema
from services.gpt.gpt_assistant_service import GPTAssistantService
from settings.settings import UserProfilesRouterSettings
from utils.logger import logger

user_profiles_router_settings = UserProfilesRouterSettings()
logging = logger(user_profiles_router_settings.USER_PROFILES_ROUTER_LOG_NAME)

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

# Create the API router
router = APIRouter(
    prefix="/users-profiles",
    tags=["user-profiles"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

assistant_service = GPTAssistantService()





@router.post(
    "/skills",
    response_model=UserEnrichedSkillsDescriptionSchema,
    description="Generate an User query based on the user's skills or knowledge."
)
async def generate_skills_query(
    request: UserProfileSkillsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserEnrichedSkillsDescriptionSchema:
    """
    Generate a User query based on the user's skills or existing knowledge.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    try:
        # Generate the skills-based description
        enriched_skills = assistant_service.generate_skills_description(request.skills)

        # Map GPT response to the API schema
        return UserEnrichedSkillsDescriptionSchema(
            input_skills=request.skills,
            enriched_description=enriched_skills.generated_query
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate skills-based description: {str(e)}"
        )


@router.post(
    "/interests",
    response_model=UserEnrichedInterestsDescriptionSchema,
    description="Generate an SDG query based on the user's interests or aspirations."
)
async def generate_interests_query(
    request: UserProfileInterestsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> BaseModel:
    """
    Generate a user query based on the user's interests or aspirations.
    """
    user = verify_token(token, db)  # Ensure user is authenticated

    try:
        # Generate the interests-based description
        enriched_interests = assistant_service.generate_interests_description(request.interests)

        # Map GPT response to the API schema
        return UserEnrichedInterestsDescriptionSchema(
            input_interests=request.interests,
            enriched_description=enriched_interests.generated_query
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interests-based description: {str(e)}"
        )
