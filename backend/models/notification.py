from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str  # info, success, warning, error
    action_url: Optional[str] = None

class NotificationInDB(NotificationCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    action_url: Optional[str]
    is_read: bool
    created_at: datetime
