from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AmazonSyncLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operation: str  # create_listing, update_inventory, get_orders, update_price
    product_id: Optional[str] = None
    amazon_listing_id: Optional[str] = None  # SKU or ASIN
    feed_id: Optional[str] = None
    status: str  # pending, processing, success, failed, retry
    request_data: Dict[Any, Any]
    response_data: Optional[Dict[Any, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class SyncLogResponse(BaseModel):
    id: str
    operation: str
    product_id: Optional[str]
    amazon_listing_id: Optional[str]
    feed_id: Optional[str]
    status: str
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    completed_at: Optional[datetime]

class DeadLetterQueueItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sync_log_id: str
    operation: str
    error_message: str
    request_data: Dict[Any, Any]
    failed_at: datetime = Field(default_factory=datetime.utcnow)
    attempts: int
