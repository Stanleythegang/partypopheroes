from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class CartItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int
    image_url: Optional[str] = None
    seller_id: str
    seller_name: str

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CartResponse(BaseModel):
    items: List[CartItem]
    total_items: int
    subtotal: float
    tax: float
    total: float
