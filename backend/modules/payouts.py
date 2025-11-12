from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import logging

from models.payout import (
    StripeAccountCreate,
    StripeAccountInDB,
    PayoutCreate,
    PayoutInDB,
    PayoutResponse,
    BalanceResponse
)
from models.user import UserInDB
from modules.auth import get_current_user
from utils.stripe_service import stripe_service
from modules.notifications import create_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payouts", tags=["Payouts"])

# Database instance
db = None

def set_db(database):
    global db
    db = database

@router.post("/connect/account", status_code=status.HTTP_201_CREATED)
async def create_stripe_account(
    account_data: StripeAccountCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create Stripe Connect account for seller"""
    # Check if account already exists
    existing = await db.stripe_accounts.find_one({"user_id": current_user.id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe account already exists"
        )
    
    # Create Stripe Connect account
    stripe_account = await stripe_service.create_connect_account(
        email=account_data.email,
        country=account_data.country,
        business_type=account_data.business_type
    )
    
    # Save to database
    account_db = StripeAccountInDB(
        user_id=current_user.id,
        stripe_account_id=stripe_account['id'],
        status="pending",
        country=stripe_account['country'],
        email=stripe_account['email'],
        business_type=stripe_account['business_type'],
        charges_enabled=stripe_account.get('charges_enabled', False),
        payouts_enabled=stripe_account.get('payouts_enabled', False)
    )
    
    await db.stripe_accounts.insert_one(account_db.dict())
    
    # Create notification
    await create_notification(
        user_id=current_user.id,
        title="Stripe Account Created",
        message="Your Stripe Connect account has been created. Complete onboarding to start receiving payouts.",
        notification_type="success",
        action_url="/seller/payouts"
    )
    
    logger.info(f"✅ Stripe account created for {current_user.email}")
    
    return {
        "account_id": stripe_account['id'],
        "status": "pending",
        "message": "Stripe account created successfully"
    }

@router.get("/connect/onboarding-link")
async def get_onboarding_link(current_user: UserInDB = Depends(get_current_user)):
    """Get Stripe Connect onboarding link"""
    account = await db.stripe_accounts.find_one({"user_id": current_user.id})
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe account not found. Create one first."
        )
    
    # Generate onboarding link
    link = await stripe_service.create_account_link(
        account_id=account['stripe_account_id'],
        refresh_url="https://yourapp.com/seller/payouts/refresh",
        return_url="https://yourapp.com/seller/payouts/success"
    )
    
    return {
        "url": link['url'],
        "expires_at": link['expires_at']
    }

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(current_user: UserInDB = Depends(get_current_user)):
    """Get seller's balance"""
    account = await db.stripe_accounts.find_one({"user_id": current_user.id})
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe account not found"
        )
    
    balance = await stripe_service.get_account_balance(account['stripe_account_id'])
    
    return BalanceResponse(
        available=balance['available'],
        pending=balance['pending'],
        currency=balance['currency']
    )

@router.post("/request", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def request_payout(
    payout_data: PayoutCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Request payout to bank account"""
    account = await db.stripe_accounts.find_one({"user_id": current_user.id})
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stripe account not found"
        )
    
    if not account['payouts_enabled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payouts not enabled. Complete account verification."
        )
    
    # Check balance
    balance = await stripe_service.get_account_balance(account['stripe_account_id'])
    if balance['available'] < payout_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: ${balance['available']}"
        )
    
    # Create payout
    stripe_payout = await stripe_service.create_payout(
        account_id=account['stripe_account_id'],
        amount=payout_data.amount,
        currency=payout_data.currency,
        description=payout_data.description
    )
    
    # Save to database
    payout_db = PayoutInDB(
        user_id=current_user.id,
        stripe_payout_id=stripe_payout['id'],
        amount=payout_data.amount,
        currency=payout_data.currency,
        description=payout_data.description,
        status=stripe_payout['status'],
        arrival_date=datetime.fromisoformat(stripe_payout['arrival_date']) if stripe_payout.get('arrival_date') else None
    )
    
    await db.payouts.insert_one(payout_db.dict())
    
    # Create notification
    await create_notification(
        user_id=current_user.id,
        title="Payout Requested",
        message=f"Your payout of ${payout_data.amount} has been requested and will arrive in 2-3 business days.",
        notification_type="success"
    )
    
    logger.info(f"✅ Payout requested: ${payout_data.amount} for {current_user.email}")
    
    return PayoutResponse(**payout_db.dict())

@router.get("/history", response_model=List[PayoutResponse])
async def get_payout_history(
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get payout history"""
    payouts = await db.payouts.find({"user_id": current_user.id}).sort("created_at", -1).limit(limit).to_list(limit)
    return [PayoutResponse(**p) for p in payouts]

@router.get("/account/status")
async def get_account_status(current_user: UserInDB = Depends(get_current_user)):
    """Get Stripe account status"""
    account = await db.stripe_accounts.find_one({"user_id": current_user.id})
    
    if not account:
        return {
            "connected": False,
            "message": "No Stripe account connected"
        }
    
    # Get status from Stripe
    status_data = await stripe_service.get_account_status(account['stripe_account_id'])
    
    # Update local database
    await db.stripe_accounts.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "charges_enabled": status_data['charges_enabled'],
            "payouts_enabled": status_data['payouts_enabled'],
            "status": "active" if status_data['details_submitted'] else "pending",
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "connected": True,
        "account_id": account['stripe_account_id'],
        "charges_enabled": status_data['charges_enabled'],
        "payouts_enabled": status_data['payouts_enabled'],
        "status": "active" if status_data['details_submitted'] else "pending",
        "requirements": status_data.get('requirements', {})
    }
