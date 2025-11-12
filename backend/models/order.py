from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    quantity: int
    image_url: Optional[str] = None
    seller_id: str
    seller_name: str

class ShippingAddress(BaseModel):
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: str

class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str = "card"
    stripe_payment_intent_id: Optional[str] = None

class OrderInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str
    user_id: str
    user_email: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    subtotal: float
    tax: float
    shipping_cost: float
    total: float
    status: str = "pending"  # pending, processing, shipped, delivered, cancelled
    payment_status: str = "pending"  # pending, paid, failed, refunded
    payment_method: str
    stripe_payment_intent_id: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderResponse(BaseModel):
    id: str
    order_number: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    subtotal: float
    tax: float
    shipping_cost: float
    total: float
    status: str
    payment_status: str
    tracking_number: Optional[str]
    created_at: datetime
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]

class OrderStatusUpdate(BaseModel):
    status: str
    tracking_number: Optional[str] = None
