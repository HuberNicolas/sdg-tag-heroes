from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models import SDGCoinWallet, SDGCoinWalletHistory
from request_models.sdg_coin_wallet import WalletIncrementRequest
from schemas.sdg_coin_wallet import SDGCoinWalletSchemaFull
from schemas.sdg_coin_wallet_history import SDGCoinWalletHistorySchemaFull, NoSDGCoinWalletHistorySchemaBase
from settings.settings import CoinWalletsRouterSettings
from utils.logger import logger

# Setup Logging
coin_wallets_router_settings = CoinWalletsRouterSettings()
logging = logger(coin_wallets_router_settings.COIN_WALLETS_ROUTER_LOG_NAME)


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
    prefix="/wallets",
    tags=["Wallets"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get("/users/{user_id}/wallet", response_model=SDGCoinWalletSchemaFull,
            description="Retrieve the wallet for a specific user")
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

        return SDGCoinWalletSchemaFull.model_validate(wallet)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the wallet: {e}",
        )

@router.get("/latest", response_model=SDGCoinWalletHistorySchemaFull | NoSDGCoinWalletHistorySchemaBase)
async def get_latest_wallet_history(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Get the latest wallet history entries since the last checked timestamp.
    """
    try:
        # Ensure user is authenticated
        user = verify_token(token, db)
        user_id = user.user_id

        # Fetch the most recent history entry for the user
        latest_history = (
            db.query(SDGCoinWalletHistory)
            .join(SDGCoinWallet, SDGCoinWallet.sdg_coin_wallet_id == SDGCoinWalletHistory.wallet_id)
            .filter(SDGCoinWallet.user_id == user_id)
            .order_by(SDGCoinWalletHistory.timestamp.desc())
            .first()
        )

        if latest_history and latest_history.is_shown != 1: # Trap, True did not work!
            latest_history.is_shown = True
            db.commit()
            # Return the latest wallet history entry
            return SDGCoinWalletHistorySchemaFull.model_validate(latest_history)

        elif latest_history and latest_history.is_shown == 1:
            # No wallet history available for the user
            return NoSDGCoinWalletHistorySchemaBase()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the latest wallet history: {e}"
        )

@router.get("/users/wallets", response_model=List[SDGCoinWalletSchemaFull], description="Retrieve wallets for all users")
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
        sdg_coin_wallets = db.query(SDGCoinWallet).all()

        return [SDGCoinWalletSchemaFull.model_validate(sdg_coin_wallet) for sdg_coin_wallet in sdg_coin_wallets]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching all wallets",
        )


@router.post("/users/{user_id}/wallets/histories", response_model=SDGCoinWalletHistorySchemaFull,
             description="Add a wallet increment for a specific user")
async def add_wallet_increment(
    user_id: int,
    wallet_increment_data: WalletIncrementRequest,  # Use a schema for input validation
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
            wallet_id = wallet.sdg_coin_wallet_id,
            increment = wallet_increment_data.increment,
            reason = wallet_increment_data.reason,
        )
        db.add(new_history)

        # Update the wallet total
        wallet.total_coins += wallet_increment_data.increment

        db.commit()
        db.refresh(new_history)

        return SDGCoinWalletHistorySchemaFull.model_validate(new_history)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the wallet increment",
        )


@router.get("/personal", response_model=SDGCoinWalletSchemaFull,
            description="Retrieve the personal wallet for current user")
async def get_personal_wallet(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve the wallet (SDGCoinWallet) for current user by their ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_id = user.user_id

        # Query for the wallet by user ID
        wallet = db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet for user with ID {user_id} not found",
            )

        return SDGCoinWalletSchemaFull.model_validate(wallet)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the wallet: {e}",
        )
