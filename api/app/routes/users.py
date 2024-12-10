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
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)


@router.get("/", response_model=Page[UserSchemaFull], description="Retrieve users filtered by role")
async def get_users(
    role: Optional[UserRoleEnum] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve users filtered by role. If no role is specified, returns all users.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        query = db.query(User)

        if role:
            query = query.filter(User._roles.contains(f'"{role}"'))

        return sqlalchemy_paginate(query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching users",
        )
@router.post("/{user_id}/wallet/history", response_model=SDGCoinWalletHistorySchemaFull, description="Add a wallet increment for a specific user")
async def add_wallet_increment(
    user_id: int,
    wallet_increment_data: SDGCoinWalletHistorySchemaCreate,  # Use a schema for input validation
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Add a wallet increment (SDGCoinWalletHistory) for a specific user.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

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


@router.get("/{user_id}/wallet", response_model=SDGCoinWalletSchemaFull, description="Retrieve the wallet for a specific user")
async def get_user_wallet(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the wallet (SDGCoinWallet) for a specific user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

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

@router.post("/{user_id}/bank/history", response_model=SDGXPBankHistorySchemaFull, description="Add a bank increment for a specific user")
async def add_bank_increment(
    user_id: int,
    bank_increment_data: SDGXPBankHistorySchemaCreate,  # Use a schema for input validation
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


@router.get("/{user_id}/bank", response_model=SDGXPBankSchemaFull, description="Retrieve the bank for a specific user")
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

@router.get("/{user_id}", response_model=UserSchemaFull, description="Retrieve a specific user by ID")
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve a specific user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query for the user by ID
        user_instance = db.query(User).filter(User.user_id == user_id).first()

        if not user_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return user_instance

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the user",
        )

