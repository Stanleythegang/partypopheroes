# 🚀 Milestone 4: Buyer & Marketplace Experience

## Overview
Transform Hamro into a complete e-commerce marketplace with buyer-facing features, cart/checkout, order management, and review system.

---

## 📋 Scope

### 1. Buyer Storefront
- **Homepage**: Hero section, featured products, categories, trending items
- **Product Catalog**: Search, filters (price, category, rating), pagination
- **Product Detail**: Images, description, reviews, add to cart, related products
- **Category Pages**: Browse by category with filters
- **Search**: Full-text search with autocomplete

### 2. Shopping Cart & Checkout
- **Cart Page**: View items, update quantities, remove items
- **Cart Persistence**: Save cart to database for logged-in users
- **Guest Cart**: Session-based cart for non-logged-in users
- **Checkout Flow**:
  - Shipping address form
  - Payment with Stripe (test mode)
  - Order confirmation
  - Email receipt (mock)

### 3. Order Management
- **Buyer View**:
  - Order history
  - Order details
  - Track shipment
  - Cancel order (if not shipped)
  - Review products

- **Seller View**:
  - Incoming orders dashboard
  - Order details
  - Update status (processing, shipped, delivered)
  - Add tracking number
  - Order analytics

### 4. Review & Rating System
- **Submit Review**: After delivery, buyers can review
- **Rating**: 1-5 stars with comment
- **Review Display**: On product page with helpful votes
- **Verified Purchase Badge**: Only buyers who purchased can review
- **Review Moderation**: Admin can delete inappropriate reviews

### 5. Enhanced Analytics
- **Sales Reports**:
  - Daily/weekly/monthly sales
  - Revenue trends
  - Top selling products
  - Category performance

- **Product Analytics**:
  - Views vs sales conversion
  - Average order value
  - Customer demographics

### 6. SEO & Mobile Optimization
- **SEO**:
  - Meta tags (title, description, keywords)
  - Open Graph tags for social sharing
  - Structured data (JSON-LD)
  - Sitemap generation
  - Canonical URLs

- **Mobile Optimization**:
  - Responsive design (already implemented)
  - Touch-friendly UI
  - Mobile menu
  - Fast loading
  - PWA features (optional)

---

## 🗄️ Database Models

### Cart Collection
```javascript
{
  id: String,
  user_id: String,
  items: [{
    product_id: String,
    title: String,
    price: Float,
    quantity: Integer,
    image_url: String,
    seller_id: String,
    seller_name: String
  }],
  created_at: DateTime,
  updated_at: DateTime
}
```

### Orders Collection
```javascript
{
  id: String,
  order_number: String,
  user_id: String,
  user_email: String,
  items: [OrderItem],
  shipping_address: {
    full_name, address_line1, city, state, postal_code, country, phone
  },
  subtotal: Float,
  tax: Float,
  shipping_cost: Float,
  total: Float,
  status: String (pending/processing/shipped/delivered/cancelled),
  payment_status: String (pending/paid/failed/refunded),
  payment_method: String,
  stripe_payment_intent_id: String,
  tracking_number: String,
  created_at: DateTime,
  shipped_at: DateTime,
  delivered_at: DateTime
}
```

### Reviews Collection
```javascript
{
  id: String,
  product_id: String,
  user_id: String,
  user_name: String,
  rating: Integer (1-5),
  title: String,
  comment: String,
  images: [String],
  is_verified_purchase: Boolean,
  helpful_count: Integer,
  created_at: DateTime
}
```

---

## 🔌 API Endpoints (New)

### Cart
```
GET    /api/cart                 - Get user's cart
POST   /api/cart/items           - Add item to cart
PUT    /api/cart/items/{id}      - Update quantity
DELETE /api/cart/items/{id}      - Remove item
DELETE /api/cart                 - Clear cart
```

### Orders
```
POST   /api/orders               - Create order (checkout)
GET    /api/orders               - Get user's orders
GET    /api/orders/{id}          - Get order details
PUT    /api/orders/{id}/cancel   - Cancel order

# Seller endpoints
GET    /api/orders/seller        - Get seller's orders
PUT    /api/orders/{id}/status   - Update order status
```

### Reviews
```
POST   /api/reviews              - Submit review
GET    /api/reviews/product/{id} - Get product reviews
GET    /api/reviews/stats/{id}   - Get review statistics
PUT    /api/reviews/{id}/helpful - Mark review as helpful
DELETE /api/reviews/{id}         - Delete review (admin)
```

### Checkout
```
POST   /api/checkout/create-intent    - Create Stripe payment intent
POST   /api/checkout/confirm          - Confirm payment
```

---

## 🎨 Frontend Pages (New)

### Public Pages
- `/` - Homepage
- `/shop` - Product catalog
- `/shop/category/:category` - Category page
- `/product/:id` - Product detail
- `/cart` - Shopping cart
- `/checkout` - Checkout flow
- `/search?q=query` - Search results

### Buyer Pages
- `/orders` - Order history
- `/orders/:id` - Order details
- `/account/reviews` - My reviews

### Seller Pages (Enhanced)
- `/seller/orders` - Incoming orders (replace placeholder)

---

## 🏗️ Implementation Phases

### Phase 1: Backend Foundation (Day 1)
- ✅ Create models (Cart, Order, Review)
- ✅ Cart API endpoints
- ✅ Order API endpoints
- ✅ Review API endpoints
- ✅ Stripe checkout integration

### Phase 2: Buyer Storefront (Day 2)
- Homepage design
- Product catalog with search/filters
- Product detail page
- Category pages

### Phase 3: Cart & Checkout (Day 2)
- Shopping cart UI
- Checkout flow
- Payment integration
- Order confirmation

### Phase 4: Order Management (Day 3)
- Buyer order history
- Seller order dashboard
- Order status updates
- Tracking integration

### Phase 5: Reviews & Analytics (Day 3)
- Review submission
- Review display
- Enhanced analytics
- Sales reports

### Phase 6: SEO & Polish (Day 4)
- Meta tags
- Mobile optimization
- Performance tuning
- Testing

---

## 🎯 Success Criteria

✅ Buyer can browse products
✅ Add products to cart
✅ Complete checkout with Stripe test card
✅ View order history
✅ Submit product reviews
✅ Seller can view and fulfill orders
✅ Admin can manage reviews
✅ Analytics show sales data
✅ SEO tags present
✅ Mobile responsive

---

## 📊 Timeline

**Estimated**: 3-4 days
- Backend: 1 day
- Frontend: 2 days
- Testing & Polish: 1 day

**Current Progress**: 0%
**Status**: Initialized

---

## 🚀 Ready to Start!

Milestone 4 structure is set up. Let's build the complete buyer experience!
