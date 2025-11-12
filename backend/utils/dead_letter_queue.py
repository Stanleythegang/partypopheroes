import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    """
    Dead Letter Queue for failed Amazon sync operations
    """
    
    def __init__(self, db):
        self.db = db
        self.collection = db.dead_letter_queue
    
    async def add(self, sync_log_id: str, operation: str, error_message: str, request_data: Dict[Any, Any], attempts: int):
        """
        Add failed operation to DLQ
        """
        item = {
            'sync_log_id': sync_log_id,
            'operation': operation,
            'error_message': error_message,
            'request_data': request_data,
            'attempts': attempts,
            'failed_at': datetime.utcnow()
        }
        
        await self.collection.insert_one(item)
        logger.error(f"❌ Added to DLQ: {operation} (sync_log_id={sync_log_id})")
    
    async def get_items(self, limit: int = 50):
        """
        Get items from DLQ
        """
        items = await self.collection.find().sort('failed_at', -1).limit(limit).to_list(limit)
        return items
    
    async def remove(self, item_id: str):
        """
        Remove item from DLQ (after manual resolution)
        """
        result = await self.collection.delete_one({'_id': item_id})
        return result.deleted_count > 0
