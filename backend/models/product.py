from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ProductImage(BaseModel):
    url: str
    filename: str
    is_primary: bool = False

class ProductCreate(BaseModel):
    title: str
    description: str
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    sku: Optional[str] = None
    images: List[ProductImage] = []
    tags: List[str] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = None
    images: Optional[List[ProductImage]] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

class ProductInDB(ProductCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_name: str
    is_published: bool = False
    is_approved: bool = False  # Admin approval
    synced_to_amazon: bool = False
    amazon_asin: Optional[str] = None
    views: int = 0
    sales: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    price: float
    quantity: int
    sku: Optional[str]
    seller_id: str
    seller_name: str
    is_published: bool
    is_approved: bool
    synced_to_amazon: bool
    amazon_asin: Optional[str]
    images: List[ProductImage]
    tags: List[str]
    views: int
    sales: int
    created_at: datetime
    updated_at: datetime

class ProductApprovalAction(BaseModel):
    action: str  # approve, reject
    notes: Optional[str] = None

class AmazonSyncRequest(BaseModel):
    product_id: str

class AmazonSyncResponse(BaseModel):
    success: bool
    product_id: str
    amazon_asin: Optional[str]
    message: str
    synced_at: datetime
