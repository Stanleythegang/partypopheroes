from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])

# Placeholder models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    stock: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    stock: int = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None

# Mock data for placeholder
mock_products = [
    {
        "id": "1",
        "name": "Sample Product 1",
        "description": "This is a sample product",
        "price": 99.99,
        "category": "Electronics",
        "stock": 10,
        "created_at": datetime.utcnow()
    },
    {
        "id": "2",
        "name": "Sample Product 2",
        "description": "Another sample product",
        "price": 149.99,
        "category": "Clothing",
        "stock": 25,
        "created_at": datetime.utcnow()
    }
]

@router.get("/", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get list of products with optional filtering
    TODO: Implement actual MongoDB queries
    """
    logger.info(f"Fetching products - category: {category}, skip: {skip}, limit: {limit}")
    # Placeholder response
    return [Product(**p) for p in mock_products]

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """
    Get a single product by ID
    TODO: Implement actual MongoDB query
    """
    logger.info(f"Fetching product with ID: {product_id}")
    # Placeholder response
    if product_id in ["1", "2"]:
        product_data = next((p for p in mock_products if p["id"] == product_id), None)
        if product_data:
            return Product(**product_data)
    raise HTTPException(status_code=404, detail="Product not found")

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    """
    Create a new product
    TODO: Implement actual MongoDB insertion
    """
    logger.info(f"Creating new product: {product.name}")
    # Placeholder response
    new_product = Product(**product.dict())
    return new_product

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    """
    Update an existing product
    TODO: Implement actual MongoDB update
    """
    logger.info(f"Updating product with ID: {product_id}")
    # Placeholder response
    updated_data = {
        "id": product_id,
        "name": product.name or "Updated Product",
        "description": product.description or "Updated description",
        "price": product.price or 99.99,
        "category": product.category or "General",
        "stock": product.stock or 0,
        "created_at": datetime.utcnow()
    }
    return Product(**updated_data)

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """
    Delete a product
    TODO: Implement actual MongoDB deletion
    """
    logger.info(f"Deleting product with ID: {product_id}")
    return {"message": f"Product {product_id} deleted successfully"}
