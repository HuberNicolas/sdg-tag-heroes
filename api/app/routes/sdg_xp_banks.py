from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from models import SDGXPBank, SDGXPBankHistory
from requests_models.sdg_xp_bank import BankIncrementRequest
from schemas import SDGXPBankHistorySchemaFull, SDGXPBankSchemaFull
from api.app.routes.authentication import verify_token
from api.app.security import Security
from settings.settings import XPBanksRouterSettings
from utils.logger import logger

# Setup Logging
xp_banks_router_settings = XPBanksRouterSettings()
logging = logger(xp_banks_router_settings.XP_BANKS_ROUTER_LOG_NAME)

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
    prefix="/banks",
    tags=["Banks"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get("/users/{user_id}/bank", response_model=SDGXPBankSchemaFull,
            description="Retrieve the bank for a specific user")
async def get_user_bank(
        user_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the bank (SDGXPBank) for a specific user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query for the bank by user ID
        sdg_xp_bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()

        if not sdg_xp_bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank for user with ID {user_id} not found",
            )

        return SDGXPBankSchemaFull.model_validate(sdg_xp_bank)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the bank: {e}",
        )


@router.get("/users/banks", response_model=List[SDGXPBankSchemaFull],
            description="Retrieve banks for all users")
async def get_all_banks(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """
    Retrieve all banks (SDGXPBank) for all users.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query all banks
        sdg_xp_banks = db.query(SDGXPBank).all()

        return [SDGXPBankSchemaFull.model_validate(sdg_xp_bank) for sdg_xp_bank in sdg_xp_banks]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching all banks: {e}",
        )


@router.post("/users/{user_id}/banks/histories", response_model=SDGXPBankHistorySchemaFull,
             description="Add a bank increment for a specific user")
async def add_bank_increment(
        user_id: int,
        request: BankIncrementRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """
    Add a bank increment (SDGXPBankHistory) for a specific user.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Check if the user has a bank
        bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank for user with ID {user_id} not found",
            )

        # Determine the specific SDG XP field to update
        sdg_field = f"{request.sdg.value.lower()}_xp"
        if not hasattr(bank, sdg_field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid SDG value: {request.sdg}",
            )

        # Update the specific SDG XP
        setattr(bank, sdg_field, getattr(bank, sdg_field) + request.increment)

        # Update the total XP
        bank.total_xp += request.increment

        # Create the bank increment history entry
        new_history = SDGXPBankHistory(
            xp_bank_id=bank.sdg_xp_bank_id,
            sdg=request.sdg,
            increment=request.increment,
            reason=request.reason,
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)

        return SDGXPBankHistorySchemaFull.model_validate(new_history)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the bank increment",
        )


@router.get("/personal", response_model=SDGXPBankSchemaFull,
            description="Retrieve the personal bank for current user")
async def get_personal_bank(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the bank (SDGXPBank) for current user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user.user_id

        # Query for the bank by user ID
        sdg_xp_bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()

        if not sdg_xp_bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank for user with ID {user_id} not found",
            )

        return SDGXPBankSchemaFull.model_validate(sdg_xp_bank)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the bank: {e}",
        )
