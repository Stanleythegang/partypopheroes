from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class StripeAccountCreate(BaseModel):
    country: str = "US"
    email: str
    business_type: str = "individual"  # individual, company

class StripeAccountInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stripe_account_id: str
    status: str  # pending, active, restricted, disabled
    country: str
    email: str
    business_type: str
    charges_enabled: bool = False
    payouts_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PayoutCreate(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None

class PayoutInDB(PayoutCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stripe_payout_id: str
    status: str  # pending, paid, failed, canceled
    arrival_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

class PayoutResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    arrival_date: Optional[datetime]
    created_at: datetime
    paid_at: Optional[datetime]

class BalanceResponse(BaseModel):
    available: float
    pending: float
    currency: str
