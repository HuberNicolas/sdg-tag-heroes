from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from models import SDGRank, SDGXPBank
from models.users.user import User
from request_models.sdg_rank import UserIdsRequest
from db.mariadb_connector import engine as mariadb_engine
from schemas.sdg_ranks import UsersSDGRankSchemaBase, SDGRankSchemaBase, SDGRankSchemaFull
from schemas.users.user import UserSchemaFull
from settings.settings import SDGRanksSettings
from api.app.security import Security
from utils.logger import logger

# Setup Logging
sdg_ranks_router_settings = SDGRanksSettings()
logging = logger(sdg_ranks_router_settings.SDGRANKS_ROUTER_LOG_NAME)

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
    prefix="/ranks",
    tags=["Ranks"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get("/users/{user_id}/", response_model=List[SDGRankSchemaFull],
            description="Retrieve all SDG ranks (1-17) for a specific user based on their XP bank")
async def get_user_ranks_and_xp(
        user_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """
    Retrieve all SDG ranks (1-17) for a specific user by their user ID based on their XP bank.
    This will include the rank for each SDG by comparing the XP bank and rank requirements.
    """
    try:
        # Ensure the user is authenticated
        user = verify_token(token, db)

        # Query for all SDG ranks for the user (0 rank to 3 ranks for each SDG)
        ranks = db.query(SDGRank).filter(SDGRank.sdg_goal_id.between(1, 17)).all()

        if not ranks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ranks for user with ID {user_id} not found",
            )

        # Query for the SDG XP bank of the user
        xp_bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()

        if not xp_bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"XP bank for user with ID {user_id} not found",
            )

        # Fetch ranks and compare with user's XP to assign the correct tier (rank) for each SDG
        user_ranks = []
        for sdg_id in range(1, 18):  # For each SDG 1 through 17
            # Get the XP value for the current SDG goal
            sdg_xp = getattr(xp_bank, f"sdg{sdg_id}_xp")

            # Find the highest tier that the user's XP qualifies for
            user_rank = None
            for rank in ranks:
                if rank.sdg_goal_id == sdg_id:
                    if sdg_xp >= rank.xp_required:
                        user_rank = rank  # User qualifies for this rank tier
                    else:
                        break  # No need to check further tiers since XP is not enough

            if user_rank:
                user_ranks.append(SDGRankSchemaFull.model_validate(user_rank))
            else:
                # If no rank is found, default to tier 0 (beginning rank)
                default_rank = next((r for r in ranks if r.sdg_goal_id == sdg_id and r.tier == 0), None)
                if default_rank:
                    user_ranks.append(SDGRankSchemaFull.model_validate(default_rank))

        return user_ranks

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching ranks and XP: {e}",
        )
@router.get("/users/", response_model=List[UsersSDGRankSchemaBase], description="Retrieve ranks for all users")
async def get_ranks_for_all_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        # Ensure user is authenticated
        verify_token(token, db)

        # Query all users
        users = db.query(User).all()

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )

        # Query XP banks for all users
        user_xp_banks = db.query(SDGXPBank).filter(SDGXPBank.user_id.in_([u.user_id for u in users])).all()

        all_user_ranks = []
        for user in users:
            xp_bank = next((bank for bank in user_xp_banks if bank.user_id == user.user_id), None)

            if not xp_bank:
                continue  # Skip users without XP data

            user_ranks = []
            for sdg_id in range(1, 18):  # SDG 1-17
                sdg_xp = getattr(xp_bank, f"sdg{sdg_id}_xp")
                rank = db.query(SDGRank).filter(SDGRank.sdg_goal_id == sdg_id, SDGRank.xp_required <= sdg_xp).order_by(SDGRank.xp_required.desc()).first()

                if rank:
                    user_ranks.append(SDGRankSchemaFull.model_validate(rank))

            if user_ranks:
                user_info = UserSchemaFull.model_validate(user)
                all_user_ranks.append({
                    "user_id": user.user_id,
                    "user": user_info,
                    "ranks": user_ranks
                })

        return all_user_ranks

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDG ranks: {e}",
        )

@router.post("/users/", response_model=List[UsersSDGRankSchemaBase], description="Get SDG ranks for a list of user IDs")
async def get_sdg_ranks_for_users(
    request: UserIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Ensure user is authenticated
        verify_token(token, db)

        if not request.user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user IDs provided"
            )

        # Query users and XP banks for the provided user IDs
        users = db.query(User).filter(User.user_id.in_(request.user_ids)).all()
        user_xp_banks = db.query(SDGXPBank).filter(SDGXPBank.user_id.in_(request.user_ids)).all()

        if not users or not user_xp_banks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No SDG ranks found for the provided user IDs"
            )

        response_data = []
        for user in users:
            xp_bank = next((bank for bank in user_xp_banks if bank.user_id == user.user_id), None)

            if not xp_bank:
                continue  # Skip users without XP data

            user_ranks = []
            for sdg_id in range(1, 18):  # SDG 1-17
                sdg_xp = getattr(xp_bank, f"sdg{sdg_id}_xp")
                rank = db.query(SDGRank).filter(SDGRank.sdg_goal_id == sdg_id, SDGRank.xp_required <= sdg_xp).order_by(SDGRank.xp_required.desc()).first()

                if rank:
                    user_ranks.append(SDGRankSchemaFull.model_validate(rank))

            if user_ranks:
                user_info = UserSchemaFull.model_validate(user)
                response_data.append({
                    "user_id": user.user_id,
                    "user": user_info,
                    "ranks": user_ranks
                })

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDG ranks: {e}",
        )
