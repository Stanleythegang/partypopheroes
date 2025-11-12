from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models.amazon_sync import AmazonSyncLog, SyncLogResponse
from models.user import UserInDB
from modules.auth import get_current_user, get_admin_user
from utils.amazon_sp_api_client import amazon_client
from utils.dead_letter_queue import DeadLetterQueue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/amazon-sync", tags=["Amazon Sync"])

# Database instance
db = None
dlq = None

def set_db(database):
    global db, dlq
    db = database
    dlq = DeadLetterQueue(database)

async def create_sync_log(operation: str, request_data: dict, product_id: str = None) -> str:
    """Create sync log entry"""
    sync_log = AmazonSyncLog(
        operation=operation,
        product_id=product_id,
        status="pending",
        request_data=request_data
    )
    
    await db.amazon_sync_logs.insert_one(sync_log.dict())
    logger.info(f"📝 Sync log created: {sync_log.id} ({operation})")
    
    return sync_log.id

async def retry_failed_sync(sync_log_id: str):
    """Retry failed sync operation with backoff"""
    sync_log_data = await db.amazon_sync_logs.find_one({'id': sync_log_id})
    
    if not sync_log_data:
        return
    
    sync_log = AmazonSyncLog(**sync_log_data)
    
    if sync_log.retry_count >= sync_log.max_retries:
        # Move to DLQ
        await dlq.add(
            sync_log_id=sync_log.id,
            operation=sync_log.operation,
            error_message=sync_log.error_message,
            request_data=sync_log.request_data,
            attempts=sync_log.retry_count
        )
        
        await db.amazon_sync_logs.update_one(
            {'id': sync_log_id},
            {'$set': {'status': 'failed_max_retries'}}
        )
        
        logger.error(f"❌ Max retries exceeded for {sync_log_id}, moved to DLQ")
        return
    
    # Increment retry count
    await db.amazon_sync_logs.update_one(
        {'id': sync_log_id},
        {'$inc': {'retry_count': 1}, '$set': {'status': 'retry', 'updated_at': datetime.utcnow()}}
    )
    
    # Retry the operation
    if sync_log.operation == 'create_listing':
        await amazon_client.create_listing(sync_log.request_data, db, sync_log_id)
    elif sync_log.operation == 'update_inventory':
        await amazon_client.update_inventory(
            sync_log.request_data['sku'],
            sync_log.request_data['quantity'],
            db,
            sync_log_id
        )
    elif sync_log.operation == 'get_orders':
        await amazon_client.get_orders(db=db, sync_log_id=sync_log_id)

# Admin Endpoints
@router.get("/logs", response_model=List[SyncLogResponse])
async def get_sync_logs(
    status: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 50,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Get Amazon sync logs (Admin only)"""
    query = {}
    if status:
        query['status'] = status
    if operation:
        query['operation'] = operation
    
    logs = await db.amazon_sync_logs.find(query).sort('created_at', -1).limit(limit).to_list(limit)
    
    return [SyncLogResponse(**log) for log in logs]

@router.get("/logs/{sync_log_id}")
async def get_sync_log_detail(
    sync_log_id: str,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Get detailed sync log (Admin only)"""
    log = await db.amazon_sync_logs.find_one({'id': sync_log_id})
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync log not found"
        )
    
    return log

@router.post("/logs/{sync_log_id}/retry")
async def retry_sync_log(
    sync_log_id: str,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Retry failed sync operation (Admin only)"""
    await retry_failed_sync(sync_log_id)
    
    return {"message": "Retry initiated", "sync_log_id": sync_log_id}

@router.get("/stats")
async def get_sync_stats(admin_user: UserInDB = Depends(get_admin_user)):
    """Get sync statistics (Admin only)"""
    total = await db.amazon_sync_logs.count_documents({})
    success = await db.amazon_sync_logs.count_documents({'status': 'success'})
    failed = await db.amazon_sync_logs.count_documents({'status': 'failed'})
    pending = await db.amazon_sync_logs.count_documents({'status': 'pending'})
    processing = await db.amazon_sync_logs.count_documents({'status': 'processing'})
    
    # Last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_success = await db.amazon_sync_logs.count_documents({
        'status': 'success',
        'created_at': {'$gte': yesterday}
    })
    recent_failed = await db.amazon_sync_logs.count_documents({
        'status': 'failed',
        'created_at': {'$gte': yesterday}
    })
    
    return {
        'total': total,
        'success': success,
        'failed': failed,
        'pending': pending,
        'processing': processing,
        'last_24h': {
            'success': recent_success,
            'failed': recent_failed
        }
    }

@router.get("/dlq")
async def get_dead_letter_queue(
    limit: int = 50,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Get dead letter queue items (Admin only)"""
    items = await dlq.get_items(limit)
    return {'items': items, 'count': len(items)}

@router.delete("/dlq/{item_id}")
async def remove_from_dlq(
    item_id: str,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Remove item from DLQ (Admin only)"""
    removed = await dlq.remove(item_id)
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DLQ item not found"
        )
    
    return {"message": "Item removed from DLQ"}

# Test endpoint for sandbox
@router.post("/test/create-listing")
async def test_create_listing(current_user: UserInDB = Depends(get_current_user)):
    """Test listing creation in sandbox"""
    test_product = {
        'id': 'test-product-123',
        'title': 'Test Product for Amazon Sandbox',
        'sku': 'TEST-SKU-001',
        'price': 29.99,
        'quantity': 100,
        'brand': 'Test Brand',
        'category': 'Electronics'
    }
    
    # Create sync log
    sync_log_id = await create_sync_log(
        operation='create_listing',
        request_data=test_product,
        product_id=test_product['id']
    )
    
    # Create listing
    result = await amazon_client.create_listing(test_product, db, sync_log_id)
    
    return {
        'sync_log_id': sync_log_id,
        'result': result
    }

@router.post("/test/update-inventory")
async def test_update_inventory(current_user: UserInDB = Depends(get_current_user)):
    """Test inventory update in sandbox"""
    test_data = {
        'sku': 'TEST-SKU-001',
        'quantity': 50
    }
    
    sync_log_id = await create_sync_log(
        operation='update_inventory',
        request_data=test_data
    )
    
    result = await amazon_client.update_inventory(
        test_data['sku'],
        test_data['quantity'],
        db,
        sync_log_id
    )
    
    return {
        'sync_log_id': sync_log_id,
        'result': result
    }

@router.post("/test/get-orders")
async def test_get_orders(current_user: UserInDB = Depends(get_current_user)):
    """Test order retrieval in sandbox"""
    sync_log_id = await create_sync_log(
        operation='get_orders',
        request_data={}
    )
    
    result = await amazon_client.get_orders(db=db, sync_log_id=sync_log_id)
    
    return {
        'sync_log_id': sync_log_id,
        'result': result
    }
