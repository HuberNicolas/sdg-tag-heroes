from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker, joinedload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from db.mariadb_connector import engine as mariadb_engine
from models import User, SDGXPBank, SDGCoinWallet, SDGXPBankHistory, SDGCoinWalletHistory
from api.app.routes.authentication import verify_token
from api.app.security import Security
from schemas.sdg_coin_wallet import SDGCoinWalletSchemaFull
from schemas.sdg_coin_wallet_history import SDGCoinWalletHistorySchemaFull, SDGCoinWalletHistorySchemaCreate
from settings.settings import CoinWalletsRouterSettings
coin_wallets_router_settings = CoinWalletsRouterSettings()

# Setup OAuth2 and security
security = Security()
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger

logging = logger(coin_wallets_router_settings.COIN_WALLETS_ROUTER_LOG_NAME)

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
    prefix="/wallets",
    tags=["wallets"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.post("/history", response_model=SDGCoinWalletHistorySchemaFull, description="Add a wallet increment for a specific user")
async def add_wallet_increment(
    wallet_increment_data: SDGCoinWalletHistorySchemaCreate,  # Use a schema for input validation
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Add a wallet increment (SDGCoinWalletHistory) for a specific user.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user["user_id"]

        # Check if the user has a wallet
        wallet = db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet for user with ID {user_id} not found",
            )

        # Create the wallet increment history entry
        new_history = SDGCoinWalletHistory(
            wallet_id=wallet.sdg_coin_wallet_id,
            increment=wallet_increment_data.increment,
            reason=wallet_increment_data.reason,
        )
        db.add(new_history)

        # Update the wallet total
        wallet.total_coins += wallet_increment_data.increment

        db.commit()
        db.refresh(new_history)

        return new_history

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the wallet increment",
        )

@router.get("/latest", response_model=SDGCoinWalletHistorySchemaFull)
async def get_latest_wallet_history(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Get the latest wallet history entries since the last checked timestamp.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user["user_id"]

        # Fetch the most recent history entry for the user
        latest_history = (
            db.query(SDGCoinWalletHistory)
            .join(SDGCoinWallet, SDGCoinWallet.sdg_coin_wallet_id == SDGCoinWalletHistory.wallet_id)
            .filter(SDGCoinWallet.user_id == user_id)
            .order_by(SDGCoinWalletHistory.created_at.desc())
            .first()
        )

        if not latest_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No wallet history found for the user.",
            )
        print(latest_history)
        return latest_history
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the latest wallet history.",
        )

@router.get("/personal", response_model=SDGCoinWalletSchemaFull, description="Retrieve the wallet for a specific user")
async def get_user_wallet(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the wallet (SDGCoinWallet) for a specific user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user["user_id"]

        # Query for the wallet by user ID
        wallet = db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet for user with ID {user_id} not found",
            )

        return wallet

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the wallet",
        )

@router.get("/", response_model=Page[SDGCoinWalletSchemaFull], description="Retrieve wallets for all users")
async def get_all_wallets(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve all wallets (SDGCoinWallet) for all users.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query all wallets
        query = db.query(SDGCoinWallet)
        return sqlalchemy_paginate(query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all wallets",
        )
