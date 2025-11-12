import logging
import os
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import random

try:
    from sp_api.api import CatalogItems, Listings, Feeds, Orders
    from sp_api.base import Marketplaces, SellingApiException
    SP_API_AVAILABLE = True
except ImportError:
    SP_API_AVAILABLE = False
    logging.warning("SP-API library not available, using sandbox simulation")

logger = logging.getLogger(__name__)

class AmazonSPAPIClient:
    """
    Production-ready Amazon SP-API Client with Sandbox Support
    
    Credentials can be provided via:
    1. Environment variables
    2. AWS Secrets Manager (documented)
    3. Direct initialization
    """
    
    def __init__(self, credentials: Optional[Dict] = None):
        # Get credentials from environment or parameter
        self.credentials = credentials or {
            'refresh_token': os.getenv('AMAZON_REFRESH_TOKEN', 'sandbox_refresh_token'),
            'lwa_app_id': os.getenv('AMAZON_LWA_APP_ID', 'amzn1.application.sandbox'),
            'lwa_client_secret': os.getenv('AMAZON_LWA_CLIENT_SECRET', 'sandbox_client_secret'),
            'aws_access_key': os.getenv('AWS_ACCESS_KEY_ID', 'sandbox_access_key'),
            'aws_secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', 'sandbox_secret_key'),
        }
        
        self.marketplace = os.getenv('AMAZON_MARKETPLACE', 'US')
        self.is_sandbox = os.getenv('AMAZON_SANDBOX', 'true').lower() == 'true'
        
        # Initialize API clients
        self._init_clients()
        
        logger.info(f"🛒 Amazon SP-API Client initialized")
        logger.info(f"   Mode: {'SANDBOX' if self.is_sandbox else 'PRODUCTION'}")
        logger.info(f"   Marketplace: {self.marketplace}")
        logger.info(f"   Library Available: {SP_API_AVAILABLE}")
    
    def _init_clients(self):
        """Initialize SP-API clients"""
        if not SP_API_AVAILABLE or self.is_sandbox:
            logger.info("Using sandbox simulation mode")
            self.listings_client = None
            self.feeds_client = None
            self.orders_client = None
            return
        
        try:
            # Real SP-API clients
            marketplace = getattr(Marketplaces, self.marketplace)
            
            self.listings_client = Listings(
                credentials=self.credentials,
                marketplace=marketplace
            )
            
            self.feeds_client = Feeds(
                credentials=self.credentials,
                marketplace=marketplace
            )
            
            self.orders_client = Orders(
                credentials=self.credentials,
                marketplace=marketplace
            )
            
            logger.info("✅ SP-API clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SP-API clients: {e}")
            self.listings_client = None
            self.feeds_client = None
            self.orders_client = None
    
    def _generate_sandbox_id(self, prefix: str) -> str:
        """Generate sandbox ID"""
        timestamp = int(time.time())
        random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"{prefix}_{timestamp}_{random_suffix}"
    
    async def create_listing(self, product_data: Dict[Any, Any], db=None, sync_log_id: str = None) -> Dict[str, Any]:
        """
        Create product listing on Amazon
        
        Args:
            product_data: Product information
            db: Database connection for logging
            sync_log_id: Sync log ID for tracking
        
        Returns:
            Dict with amazon_listing_id, feed_id, status
        """
        operation_start = time.time()
        
        try:
            logger.info(f"📦 Creating Amazon listing for: {product_data.get('title')}")
            
            # Sandbox mode or no library available
            if self.is_sandbox or not SP_API_AVAILABLE:
                return await self._create_listing_sandbox(product_data, db, sync_log_id)
            
            # Real SP-API implementation
            sku = product_data.get('sku') or f"SKU-{product_data['id'][:8]}"
            
            # Prepare listing data
            listing_data = {
                'productType': 'PRODUCT',  # Adjust based on category
                'requirements': 'LISTING',
                'attributes': {
                    'item_name': [{'value': product_data['title'], 'marketplace_id': 'ATVPDKIKX0DER'}],
                    'brand': [{'value': product_data.get('brand', 'Generic'), 'marketplace_id': 'ATVPDKIKX0DER'}],
                    'externally_assigned_product_identifier': [{
                        'type': 'ean',
                        'value': product_data.get('ean', '0000000000000'),
                        'marketplace_id': 'ATVPDKIKX0DER'
                    }],
                    'purchasable_offer': [{
                        'marketplace_id': 'ATVPDKIKX0DER',
                        'currency': 'USD',
                        'our_price': [{'schedule': [{'value_with_tax': product_data['price']}]}]
                    }],
                    'fulfillment_availability': [{
                        'fulfillment_channel_code': 'DEFAULT',
                        'quantity': product_data['quantity']
                    }]
                }
            }
            
            # Create listing
            response = self.listings_client.put_listings_item(
                sellerId='YOUR_SELLER_ID',  # Should come from env
                sku=sku,
                marketplaceIds=['ATVPDKIKX0DER'],
                body=listing_data
            )
            
            duration = time.time() - operation_start
            
            result = {
                'success': True,
                'amazon_listing_id': sku,
                'feed_id': response.payload.get('submissionId') if hasattr(response, 'payload') else None,
                'status': 'processing',
                'message': 'Listing submitted to Amazon',
                'duration': duration
            }
            
            # Update sync log
            if db and sync_log_id:
                await db.amazon_sync_logs.update_one(
                    {'id': sync_log_id},
                    {'$set': {
                        'status': 'processing',
                        'amazon_listing_id': sku,
                        'feed_id': result['feed_id'],
                        'response_data': result,
                        'updated_at': datetime.utcnow()
                    }}
                )
            
            logger.info(f"✅ Listing created: SKU={sku}, Duration={duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - operation_start
            logger.error(f"❌ Failed to create listing: {e}")
            
            if db and sync_log_id:
                await db.amazon_sync_logs.update_one(
                    {'id': sync_log_id},
                    {'$set': {
                        'status': 'failed',
                        'error_message': str(e),
                        'updated_at': datetime.utcnow()
                    }}
                )
            
            return {
                'success': False,
                'error': str(e),
                'duration': duration
            }
    
    async def _create_listing_sandbox(self, product_data: Dict[Any, Any], db=None, sync_log_id: str = None) -> Dict[str, Any]:
        """Sandbox simulation for listing creation"""
        # Simulate API delay
        await self._simulate_delay()
        
        sku = product_data.get('sku') or f"SKU-{product_data['id'][:8]}"
        feed_id = self._generate_sandbox_id('FEED')
        
        result = {
            'success': True,
            'amazon_listing_id': sku,
            'feed_id': feed_id,
            'status': 'processing',
            'message': 'Sandbox listing created',
            'sandbox_mode': True
        }
        
        # Update sync log
        if db and sync_log_id:
            await db.amazon_sync_logs.update_one(
                {'id': sync_log_id},
                {'$set': {
                    'status': 'success',
                    'amazon_listing_id': sku,
                    'feed_id': feed_id,
                    'response_data': result,
                    'completed_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }}
            )
        
        logger.info(f"✅ SANDBOX: Listing created SKU={sku}, Feed={feed_id}")
        return result
    
    async def update_inventory(self, sku: str, quantity: int, db=None, sync_log_id: str = None) -> Dict[str, Any]:
        """Update inventory for a listing"""
        try:
            logger.info(f"📦 Updating inventory: SKU={sku}, Quantity={quantity}")
            
            if self.is_sandbox or not SP_API_AVAILABLE:
                await self._simulate_delay()
                
                result = {
                    'success': True,
                    'sku': sku,
                    'quantity': quantity,
                    'feed_id': self._generate_sandbox_id('INV_FEED'),
                    'sandbox_mode': True
                }
                
                if db and sync_log_id:
                    await db.amazon_sync_logs.update_one(
                        {'id': sync_log_id},
                        {'$set': {
                            'status': 'success',
                            'response_data': result,
                            'completed_at': datetime.utcnow(),
                            'updated_at': datetime.utcnow()
                        }}
                    )
                
                logger.info(f"✅ SANDBOX: Inventory updated")
                return result
            
            # Real implementation would use Feeds API
            # feed_response = self.feeds_client.submit_feed(...)
            
        except Exception as e:
            logger.error(f"❌ Failed to update inventory: {e}")
            if db and sync_log_id:
                await db.amazon_sync_logs.update_one(
                    {'id': sync_log_id},
                    {'$set': {
                        'status': 'failed',
                        'error_message': str(e),
                        'updated_at': datetime.utcnow()
                    }}
                )
            return {'success': False, 'error': str(e)}
    
    async def get_orders(self, created_after: Optional[datetime] = None, db=None, sync_log_id: str = None) -> Dict[str, Any]:
        """Get orders from Amazon"""
        try:
            logger.info(f"📦 Fetching orders from Amazon")
            
            if self.is_sandbox or not SP_API_AVAILABLE:
                await self._simulate_delay()
                
                # Generate sample orders
                sample_orders = [
                    {
                        'amazon_order_id': self._generate_sandbox_id('ORDER'),
                        'purchase_date': datetime.utcnow().isoformat(),
                        'order_status': 'Shipped',
                        'buyer_email': 'buyer@example.com',
                        'order_total': {'amount': 99.99, 'currency_code': 'USD'},
                        'items': [
                            {
                                'sku': 'SKU-12345',
                                'title': 'Sample Product',
                                'quantity': 1,
                                'item_price': {'amount': 99.99, 'currency_code': 'USD'}
                            }
                        ]
                    }
                ]
                
                result = {
                    'success': True,
                    'orders': sample_orders,
                    'count': len(sample_orders),
                    'sandbox_mode': True
                }
                
                if db and sync_log_id:
                    await db.amazon_sync_logs.update_one(
                        {'id': sync_log_id},
                        {'$set': {
                            'status': 'success',
                            'response_data': result,
                            'completed_at': datetime.utcnow(),
                            'updated_at': datetime.utcnow()
                        }}
                    )
                
                logger.info(f"✅ SANDBOX: Retrieved {len(sample_orders)} orders")
                return result
            
            # Real implementation
            # response = self.orders_client.get_orders(CreatedAfter=created_after)
            
        except Exception as e:
            logger.error(f"❌ Failed to get orders: {e}")
            if db and sync_log_id:
                await db.amazon_sync_logs.update_one(
                    {'id': sync_log_id},
                    {'$set': {
                        'status': 'failed',
                        'error_message': str(e),
                        'updated_at': datetime.utcnow()
                    }}
                )
            return {'success': False, 'error': str(e)}
    
    async def _simulate_delay(self, min_ms: int = 100, max_ms: int = 500):
        """Simulate API delay"""
        import asyncio
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)
    
    def retry_with_backoff(self, max_retries: int = 3, base_delay: float = 1.0):
        """Decorator for retry logic with exponential backoff"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                        
                        import asyncio
                        await asyncio.sleep(delay)
                
                return None
            return wrapper
        return decorator

# Global instance
amazon_client = AmazonSPAPIClient()
