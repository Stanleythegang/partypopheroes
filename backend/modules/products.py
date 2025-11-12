from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
import logging

from models.product import (
    ProductCreate,
    ProductUpdate,
    ProductInDB,
    ProductResponse,
    ProductApprovalAction,
    AmazonSyncRequest,
    AmazonSyncResponse
)
from models.user import UserInDB
from modules.auth import get_current_user, get_admin_user
from utils.amazon_sp_api import amazon_api
from modules.notifications import create_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])

# Database instance
db = None

def set_db(database):
    global db
    db = database

# Helper functions
async def get_product_by_id(product_id: str) -> Optional[ProductInDB]:
    """Get product by ID"""
    product_data = await db.products.find_one({"id": product_id})
    if product_data:
        return ProductInDB(**product_data)
    return None

async def check_product_ownership(product_id: str, user_id: str) -> bool:
    """Check if user owns the product"""
    product = await get_product_by_id(product_id)
    return product and product.seller_id == user_id

# Seller Endpoints
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new product (Seller only)"""
    logger.info(f"Creating product: {product.title} by {current_user.email}")
    
    if current_user.role not in ['seller', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can create products"
        )
    
    new_product = ProductInDB(
        **product.dict(),
        seller_id=current_user.id,
        seller_name=current_user.full_name
    )
    
    await db.products.insert_one(new_product.dict())
    logger.info(f"✅ Product created: {new_product.id}")
    
    return ProductResponse(**new_product.dict())

@router.get("/my-products", response_model=List[ProductResponse])
async def get_my_products(
    skip: int = 0,
    limit: int = 20,
    is_published: Optional[bool] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get current seller's products"""
    query = {"seller_id": current_user.id}
    if is_published is not None:
        query["is_published"] = is_published
    
    products = await db.products.find(query).skip(skip).limit(limit).to_list(limit)
    return [ProductResponse(**p) for p in products]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get single product by ID"""
    product = await get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Increment view count
    await db.products.update_one({"id": product_id}, {"$inc": {"views": 1}})
    
    return ProductResponse(**product.dict())

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update product (Owner only)"""
    if not await check_product_ownership(product_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    if product_update.is_published:
        update_data["published_at"] = datetime.utcnow()
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    
    updated_product = await get_product_by_id(product_id)
    logger.info(f"✅ Product updated: {product_id}")
    
    return ProductResponse(**updated_product.dict())

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete product (Owner only)"""
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if current_user.role != 'admin' and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this product"
        )
    
    if product.synced_to_amazon and product.amazon_asin:
        await amazon_api.delete_product_listing(product.amazon_asin)
    
    await db.products.delete_one({"id": product_id})
    logger.info(f"✅ Product deleted: {product_id}")
    
    return {"message": "Product deleted successfully"}

@router.post("/sync/amazon", response_model=AmazonSyncResponse)
async def sync_to_amazon(
    sync_request: AmazonSyncRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Sync product to Amazon (Mock)"""
    product = await get_product_by_id(sync_request.product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if not product.is_published:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product must be published")
    
    if not product.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product must be approved by admin")
    
    if product.synced_to_amazon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already synced")
    
    # Sync to Amazon
    sync_result = await amazon_api.create_listing({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': product.price,
        'quantity': product.quantity,
        'category': product.category,
        'sku': product.sku or f"SKU-{product.id[:8]}",
        'images': [img.dict() for img in product.images]
    })
    
    if sync_result['success']:
        await db.products.update_one(
            {"id": product.id},
            {"$set": {
                "synced_to_amazon": True,
                "amazon_asin": sync_result['asin'],
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Create notification
        await create_notification(
            user_id=current_user.id,
            title="Product Synced to Amazon",
            message=f"'{product.title}' successfully synced to Amazon with ASIN: {sync_result['asin']}",
            notification_type="success",
            action_url=f"/seller/products"
        )
        
        return AmazonSyncResponse(
            success=True,
            product_id=product.id,
            amazon_asin=sync_result['asin'],
            message=sync_result['message'],
            synced_at=datetime.utcnow()
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to sync")

@router.get("/admin/all", response_model=List[ProductResponse])
async def get_all_products_admin(
    skip: int = 0,
    limit: int = 50,
    is_approved: Optional[bool] = None,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Get all products (Admin only)"""
    query = {}
    if is_approved is not None:
        query["is_approved"] = is_approved
    
    products = await db.products.find(query).skip(skip).limit(limit).to_list(limit)
    return [ProductResponse(**p) for p in products]

@router.post("/admin/{product_id}/approve")
async def approve_product(
    product_id: str,
    action: ProductApprovalAction,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Approve or reject product (Admin only)"""
    product = await get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if action.action not in ["approve", "reject"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")
    
    is_approved = action.action == "approve"
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "is_approved": is_approved,
            "approved_at": datetime.utcnow() if is_approved else None,
            "approved_by": admin_user.id if is_approved else None,
            "updated_at": datetime.utcnow()
        }}
    )
    
    logger.info(f"✅ Product {action.action}d: {product_id}")
    
    return {
        "message": f"Product {action.action}d successfully",
        "product_id": product_id,
        "is_approved": is_approved
    }

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None
):
    """List published and approved products (Public)"""
    query = {"is_published": True, "is_approved": True}
    
    if category:
        query["category"] = category
    
    products = await db.products.find(query).skip(skip).limit(limit).to_list(limit)
    return [ProductResponse(**p) for p in products]

@router.get("/analytics/seller-stats")
async def get_seller_stats(current_user: UserInDB = Depends(get_current_user)):
    """Get seller analytics"""
    total_products = await db.products.count_documents({"seller_id": current_user.id})
    published_products = await db.products.count_documents({"seller_id": current_user.id, "is_published": True})
    approved_products = await db.products.count_documents({"seller_id": current_user.id, "is_approved": True})
    synced_products = await db.products.count_documents({"seller_id": current_user.id, "synced_to_amazon": True})
    
    pipeline = [
        {"$match": {"seller_id": current_user.id}},
        {"$group": {"_id": None, "total_views": {"$sum": "$views"}, "total_sales": {"$sum": "$sales"}}}
    ]
    
    result = await db.products.aggregate(pipeline).to_list(1)
    total_views = result[0]["total_views"] if result else 0
    total_sales = result[0]["total_sales"] if result else 0
    
    category_pipeline = [
        {"$match": {"seller_id": current_user.id}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    
    categories = await db.products.aggregate(category_pipeline).to_list(100)
    
    return {
        "total_products": total_products,
        "published_products": published_products,
        "approved_products": approved_products,
        "synced_to_amazon": synced_products,
        "total_views": total_views,
        "total_sales": total_sales,
        "products_by_category": [{"category": c["_id"], "count": c["count"]} for c in categories]
    }
