from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class KYCDocument(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    encrypted: bool = True
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class KYCApplicationCreate(BaseModel):
    business_name: str
    business_type: str  # individual, company, partnership
    tax_id: Optional[str] = None
    address: str
    city: str
    state: str
    country: str
    postal_code: str

class KYCApplicationInDB(KYCApplicationCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    status: str = "pending"  # pending, approved, rejected, under_review
    id_document: Optional[KYCDocument] = None
    business_document: Optional[KYCDocument] = None
    additional_documents: List[KYCDocument] = []
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class KYCApplicationResponse(BaseModel):
    id: str
    user_id: str
    business_name: str
    business_type: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class KYCReviewAction(BaseModel):
    action: str  # approve, reject
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
