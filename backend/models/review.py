from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(ge=1, le=5)
    title: str
    comment: str
    images: List[str] = []

class ReviewInDB(ReviewCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    is_verified_purchase: bool = False
    helpful_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_name: str
    rating: int
    title: str
    comment: str
    images: List[str]
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime

class ReviewStats(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {5: 100, 4: 50, 3: 20, 2: 5, 1: 2}
