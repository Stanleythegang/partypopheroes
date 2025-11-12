from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import logging

from models.notification import (
    NotificationCreate,
    NotificationInDB,
    NotificationResponse
)
from models.user import UserInDB
from modules.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Database instance
db = None

def set_db(database):
    global db
    db = database

async def create_notification(user_id: str, title: str, message: str, notification_type: str = "info", action_url: str = None):
    """Helper function to create notifications"""
    notification = NotificationInDB(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        action_url=action_url
    )
    await db.notifications.insert_one(notification.dict())
    logger.info(f"🔔 Notification created for user {user_id}: {title}")
    return notification

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get user's notifications"""
    query = {"user_id": current_user.id}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [NotificationResponse(**n) for n in notifications]

@router.get("/unread-count")
async def get_unread_count(current_user: UserInDB = Depends(get_current_user)):
    """Get count of unread notifications"""
    count = await db.notifications.count_documents({
        "user_id": current_user.id,
        "is_read": False
    })
    return {"count": count}

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Mark notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
async def mark_all_read(current_user: UserInDB = Depends(get_current_user)):
    """Mark all notifications as read"""
    result = await db.notifications.update_many(
        {"user_id": current_user.id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"message": f"{result.modified_count} notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete notification"""
    result = await db.notifications.delete_one({
        "id": notification_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted"}
