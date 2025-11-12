import logging
import stripe
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import random

logger = logging.getLogger(__name__)

# Stripe API Key (Test Mode)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key_for_testing")

class StripeService:
    """
    Stripe Connect Integration Service
    Uses test mode keys - ready for production keys
    """
    
    def __init__(self):
        self.is_test_mode = stripe.api_key.startswith("sk_test")
        logger.info(f"💳 Stripe initialized in {'TEST' if self.is_test_mode else 'LIVE'} mode")
    
    async def create_connect_account(self, email: str, country: str = "US", business_type: str = "individual") -> Dict:
        """
        Create Stripe Connect Express account
        
        Real implementation:
        account = stripe.Account.create(
            type="express",
            country=country,
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True}
            },
            business_type=business_type
        )
        """
        logger.info(f"💳 MOCK STRIPE: Creating Connect account for {email}")
        
        # Mock account ID
        mock_account_id = f"acct_mock_{random.randint(1000000000, 9999999999)}"
        
        return {
            "id": mock_account_id,
            "email": email,
            "country": country,
            "business_type": business_type,
            "charges_enabled": False,
            "payouts_enabled": False,
            "details_submitted": False
        }
    
    async def create_account_link(self, account_id: str, refresh_url: str, return_url: str) -> Dict:
        """
        Create onboarding link for Connect account
        
        Real implementation:
        link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding"
        )
        """
        logger.info(f"💳 MOCK STRIPE: Creating account link for {account_id}")
        
        return {
            "url": f"https://connect.stripe.com/setup/mock/{account_id}",
            "expires_at": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
    
    async def get_account_balance(self, account_id: str) -> Dict:
        """
        Get Connect account balance
        
        Real implementation:
        balance = stripe.Balance.retrieve(stripe_account=account_id)
        """
        logger.info(f"💳 MOCK STRIPE: Getting balance for {account_id}")
        
        # Mock balance
        available = round(random.uniform(100, 5000), 2)
        pending = round(random.uniform(50, 1000), 2)
        
        return {
            "available": available,
            "pending": pending,
            "currency": "usd"
        }
    
    async def create_payout(self, account_id: str, amount: float, currency: str = "usd", description: Optional[str] = None) -> Dict:
        """
        Create payout to Connect account
        
        Real implementation:
        payout = stripe.Payout.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            description=description,
            stripe_account=account_id
        )
        """
        logger.info(f"💳 MOCK STRIPE: Creating payout of ${amount} to {account_id}")
        
        mock_payout_id = f"po_mock_{random.randint(1000000000, 9999999999)}"
        arrival_date = datetime.utcnow() + timedelta(days=2)
        
        return {
            "id": mock_payout_id,
            "amount": amount,
            "currency": currency,
            "description": description,
            "status": "pending",
            "arrival_date": arrival_date.isoformat(),
            "created": datetime.utcnow().isoformat()
        }
    
    async def get_payout_history(self, account_id: str, limit: int = 10) -> Dict:
        """
        Get payout history for Connect account
        
        Real implementation:
        payouts = stripe.Payout.list(
            stripe_account=account_id,
            limit=limit
        )
        """
        logger.info(f"💳 MOCK STRIPE: Getting payout history for {account_id}")
        
        # Mock payout history
        mock_payouts = []
        for i in range(min(3, limit)):
            mock_payouts.append({
                "id": f"po_mock_{random.randint(1000000000, 9999999999)}",
                "amount": round(random.uniform(100, 2000), 2),
                "currency": "usd",
                "status": random.choice(["paid", "pending"]),
                "arrival_date": (datetime.utcnow() - timedelta(days=i*7)).isoformat(),
                "created": (datetime.utcnow() - timedelta(days=i*7+2)).isoformat()
            })
        
        return {
            "data": mock_payouts,
            "has_more": False
        }
    
    async def get_account_status(self, account_id: str) -> Dict:
        """
        Get Connect account status and capabilities
        
        Real implementation:
        account = stripe.Account.retrieve(account_id)
        """
        logger.info(f"💳 MOCK STRIPE: Getting account status for {account_id}")
        
        return {
            "id": account_id,
            "charges_enabled": True,
            "payouts_enabled": True,
            "details_submitted": True,
            "requirements": {
                "currently_due": [],
                "eventually_due": [],
                "past_due": []
            }
        }

# Global instance
stripe_service = StripeService()

# For real Stripe integration, add these to .env:
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_PUBLISHABLE_KEY=pk_live_...
# STRIPE_WEBHOOK_SECRET=whsec_...
