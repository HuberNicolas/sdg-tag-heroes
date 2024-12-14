from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from db.mariadb_connector import engine as mariadb_engine
from models import User, SDGXPBank, SDGCoinWallet, SDGXPBankHistory, SDGCoinWalletHistory
from api.app.routes.authentication import verify_token
from api.app.security import Security
from schemas.sdg_coin_wallet import SDGCoinWalletSchemaFull
from schemas.sdg_coin_wallet_history import SDGCoinWalletHistorySchemaFull, SDGCoinWalletHistorySchemaCreate
from schemas.sdg_xp_bank import SDGXPBankSchemaFull
from schemas.sdg_xp_bank_history import SDGXPBankHistorySchemaCreate, SDGXPBankHistorySchemaFull
from schemas.users.user import UserSchemaFull, UserRoleEnum
from settings.settings import XPBanksRouterSettings
xp_banks_router_settings = XPBanksRouterSettings()


# Setup OAuth2 and security
security = Security()
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(xp_banks_router_settings.XP_BANKS_ROUTER_LOG_NAME)

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
    tags=["banks"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.post("/history", response_model=SDGXPBankHistorySchemaFull, description="Add a bank increment for a specific user")
async def add_bank_increment(
    bank_increment_data: SDGXPBankHistorySchemaCreate,  # Use a schema for input validation
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Add a bank increment (SDGXPBankHistory) for a specific user.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user["user_id"]
        # Check if the user has a bank
        bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank for user with ID {user_id} not found",
            )

        # Determine the specific SDG XP field to update
        sdg_field = f"{bank_increment_data.sdg.value.lower()}_xp"
        if not hasattr(bank, sdg_field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid SDG value: {bank_increment_data.sdg}",
            )

        # Update the specific SDG XP
        setattr(bank, sdg_field, getattr(bank, sdg_field) + bank_increment_data.increment)

        # Update the total XP
        bank.total_xp += bank_increment_data.increment

        # Create the bank increment history entry
        new_history = SDGXPBankHistory(
            xp_bank_id=bank.sdg_xp_bank_id,
            sdg=bank_increment_data.sdg,
            increment=bank_increment_data.increment,
            reason=bank_increment_data.reason,
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)

        return new_history

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the bank increment",
        )


@router.get("/personal", response_model=SDGXPBankSchemaFull, description="Retrieve the bank for a specific user")
async def get_user_bank(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the bank (SDGXPBank) for a specific user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user["user_id"]

        # Query for the bank by user ID
        bank = db.query(SDGXPBank).filter(SDGXPBank.user_id == user_id).first()

        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank for user with ID {user_id} not found",
            )

        return bank

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the bank",
        )

@router.get("/", response_model=Page[SDGXPBankSchemaFull], description="Retrieve banks for all users")
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
        query = db.query(SDGXPBank)
        return sqlalchemy_paginate(query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all banks",
        )


