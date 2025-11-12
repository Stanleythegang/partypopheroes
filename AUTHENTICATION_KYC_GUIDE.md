# Authentication & KYC Implementation Guide

## 🎉 Implementation Complete!

The Hamro platform now includes a complete authentication system with seller onboarding and KYC verification.

---

## 📋 Features Implemented

### ✅ Authentication System
1. **User Registration**
   - Email + Password with validation
   - Optional phone number
   - Password hashing with bcrypt
   - Automatic email verification link generation

2. **Email Verification**
   - Secure token-based verification
   - Mock email service (logs verification links)
   - Token expiration handling

3. **Phone OTP Verification**
   - 6-digit OTP generation
   - 10-minute expiration
   - Mock SMS service (logs OTP codes)

4. **JWT Authentication**
   - Access tokens (30 min expiry)
   - Refresh tokens (7 days expiry)
   - Token rotation on refresh
   - Secure token storage

5. **User Management**
   - Profile viewing and editing
   - Role-based access (user, seller, admin)
   - Account status tracking

### ✅ KYC (Know Your Customer) System
1. **Document Upload**
   - ID document (required)
   - Business document (required)
   - Additional documents (optional)
   - Supported formats: PDF, JPG, PNG

2. **File Security**
   - Client-side file validation
   - Server-side encryption (Fernet)
   - Encrypted storage in `/app/backend/storage/kyc/`
   - Secure filename hashing

3. **KYC Application**
   - Business information collection
   - Address verification
   - Tax ID (optional)
   - Status tracking (pending, approved, rejected, under_review)

4. **Admin Review Panel**
   - List all KYC applications
   - Filter by status
   - View application details
   - Download encrypted documents
   - Approve/reject with notes
   - Email notifications on status change

---

## 🔌 API Endpoints

### Authentication Endpoints

```bash
# Register new user
POST /api/auth/register
Body: {
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone": "+1234567890"  # optional
}

# Login
POST /api/auth/login
Body: {
  "email": "user@example.com",
  "password": "SecurePass123"
}
Response: {
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}

# Verify email
POST /api/auth/verify-email
Body: {
  "token": "verification_token_from_email"
}

# Send OTP to phone
POST /api/auth/send-otp
Headers: Authorization: Bearer <access_token>
Body: {
  "phone": "+1234567890"
}

# Verify OTP
POST /api/auth/verify-otp
Headers: Authorization: Bearer <access_token>
Body: {
  "phone": "+1234567890",
  "otp": "123456"
}

# Refresh token
POST /api/auth/refresh
Body: {
  "refresh_token": "..."
}

# Get current user
GET /api/auth/me
Headers: Authorization: Bearer <access_token>

# Logout
POST /api/auth/logout
Headers: Authorization: Bearer <access_token>
Body: {
  "refresh_token": "..."
}
```

### KYC Endpoints

```bash
# Submit KYC application
POST /api/kyc/apply
Headers: Authorization: Bearer <access_token>
Content-Type: multipart/form-data
Form fields:
  - business_name
  - business_type (individual/company/partnership)
  - tax_id (optional)
  - address
  - city
  - state
  - country
  - postal_code
  - id_document (file)
  - business_document (file)

# Get my KYC application
GET /api/kyc/my-application
Headers: Authorization: Bearer <access_token>

# List all applications (Admin only)
GET /api/kyc/applications?status_filter=pending
Headers: Authorization: Bearer <admin_access_token>

# Get application details (Admin only)
GET /api/kyc/applications/{kyc_id}
Headers: Authorization: Bearer <admin_access_token>

# Download KYC document (Admin only)
GET /api/kyc/download/{kyc_id}/{document_type}
Headers: Authorization: Bearer <admin_access_token>
document_type: id_document | business_document | additional_0

# Review KYC application (Admin only)
POST /api/kyc/review/{kyc_id}
Headers: Authorization: Bearer <admin_access_token>
Body: {
  "action": "approve" | "reject",
  "notes": "Optional review notes",
  "rejection_reason": "Required if rejecting"
}

# Get KYC statistics (Admin only)
GET /api/kyc/stats
Headers: Authorization: Bearer <admin_access_token>
```

---

## 🧪 Testing the Implementation

### 1. Test User Registration

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@hamro.com",
    "password": "SecurePass123",
    "full_name": "Jane Seller",
    "phone": "+1234567890"
  }'
```

**Expected**: User created, check backend logs for verification link

### 2. Test Login

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@hamro.com",
    "password": "SecurePass123"
  }'
```

**Expected**: Returns access_token and refresh_token

### 3. Test Email Verification

Check backend logs for verification token, then:

```bash
curl -X POST http://localhost:8001/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_LOGS"
  }'
```

### 4. Test KYC Submission

```bash
curl -X POST http://localhost:8001/api/kyc/apply \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "business_name=Jane's Store" \
  -F "business_type=individual" \
  -F "address=123 Main St" \
  -F "city=New York" \
  -F "state=NY" \
  -F "country=USA" \
  -F "postal_code=10001" \
  -F "id_document=@/path/to/id.pdf" \
  -F "business_document=@/path/to/business.pdf"
```

### 5. Run Unit Tests

```bash
cd /app/backend
PYTHONPATH=/app/backend python tests/test_auth.py
```

**Expected**: All tests pass ✅

---

## 🎨 Frontend Pages

### Public Pages
- **Home** (`/`) - Landing page with features
- **Register** (`/register`) - User registration form
- **Login** (`/login`) - User login form
- **Verify Email** (`/verify-email?token=...`) - Email verification

### Authenticated Pages
- **Dashboard** (`/dashboard`) - User profile and overview
- **Verify Phone** (`/verify-phone`) - Phone OTP verification
- **KYC Application** (`/kyc`) - Submit seller KYC documents

### Admin Pages
- **Admin KYC Dashboard** (`/admin/kyc`) - Review KYC applications

---

## 🔐 Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum password requirements
- Secure password comparison

### Token Security
- JWT with HS256 algorithm
- Short-lived access tokens (30 min)
- Long-lived refresh tokens (7 days)
- Token rotation on refresh
- Revocation support

### File Security
- Encrypted file storage (Fernet encryption)
- Secure filename hashing
- File type validation
- Size limits (10MB per file)
- Encrypted at rest

### Authentication Flow
1. User registers → Email verification sent
2. User verifies email → Account activated
3. User logs in → Access + refresh tokens issued
4. User optionally verifies phone → OTP sent
5. Tokens expire → Refresh to get new tokens

### KYC Flow
1. User uploads documents → Files encrypted and stored
2. Admin reviews application → Can download/view docs
3. Admin approves/rejects → User notified via email
4. Status updated → User can check in dashboard

---

## 🗄️ Database Schema

### Users Collection
```javascript
{
  id: String (UUID),
  email: String (unique),
  hashed_password: String,
  full_name: String,
  phone: String (optional),
  is_active: Boolean,
  is_verified: Boolean,
  phone_verified: Boolean,
  role: String (user/seller/admin),
  verification_token: String (nullable),
  phone_otp: String (nullable),
  phone_otp_expires: DateTime (nullable),
  created_at: DateTime,
  updated_at: DateTime
}
```

### KYC Applications Collection
```javascript
{
  id: String (UUID),
  user_id: String (FK),
  business_name: String,
  business_type: String,
  tax_id: String (optional),
  address: String,
  city: String,
  state: String,
  country: String,
  postal_code: String,
  id_document: {
    filename: String,
    original_filename: String,
    file_path: String,
    file_size: Number,
    encrypted: Boolean,
    uploaded_at: DateTime
  },
  business_document: {...},
  additional_documents: [{...}],
  status: String (pending/approved/rejected/under_review),
  submitted_at: DateTime,
  reviewed_at: DateTime (nullable),
  reviewed_by: String (nullable),
  review_notes: String (nullable),
  rejection_reason: String (nullable)
}
```

### Refresh Tokens Collection
```javascript
{
  id: String (UUID),
  user_id: String (FK),
  token: String,
  expires_at: DateTime,
  is_revoked: Boolean,
  created_at: DateTime
}
```

---

## 📱 Frontend Flow Examples

### Registration Flow
1. User fills registration form
2. Frontend sends POST to `/api/auth/register`
3. Backend creates user and sends mock verification email
4. User is redirected to login
5. User checks backend logs for verification link
6. User clicks verification link → redirected to `/verify-email?token=...`
7. Account activated

### KYC Flow
1. Seller logs in
2. Navigates to `/kyc`
3. Fills business information
4. Uploads ID and business documents
5. Frontend sends multipart POST to `/api/kyc/apply`
6. Backend encrypts and stores files
7. Application status set to "pending"
8. Admin reviews in `/admin/kyc`
9. Admin approves/rejects
10. Seller notified via mock email

---

## 🔧 Mock Services

### Mock Email Service
- Logs email content to backend console
- Shows verification links and tokens
- Simulates SendGrid/AWS SES

**Example output:**
```
📧 MOCK EMAIL SENT to user@example.com
🔗 Verification link: http://localhost:3000/verify-email?token=ABC123
🎫 Token: ABC123
```

### Mock SMS Service
- Logs OTP to backend console
- Shows phone number and code
- Simulates Twilio/AWS SNS

**Example output:**
```
📱 MOCK SMS SENT to +1234567890
🔢 OTP: 123456
```

---

## 🚀 Deployment Considerations

### Environment Variables
```bash
# Backend
SECRET_KEY=your-secret-jwt-key-here
ENCRYPTION_KEY=your-fernet-encryption-key
MONGO_URL=mongodb://localhost:27017/
DB_NAME=hamro_production

# Frontend
REACT_APP_BACKEND_URL=https://your-api-domain.com
```

### Production Checklist
- [ ] Replace mock email service with SendGrid/AWS SES
- [ ] Replace mock SMS service with Twilio/AWS SNS
- [ ] Move encrypted files to AWS S3
- [ ] Use environment-specific encryption keys
- [ ] Enable HTTPS only
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add CAPTCHA to registration
- [ ] Set up log monitoring
- [ ] Configure backup for KYC files

---

## 🎯 Testing Checklist

### Manual Testing
- [ ] Register new user
- [ ] Verify email (check logs for link)
- [ ] Login with credentials
- [ ] View dashboard
- [ ] Send OTP to phone (check logs)
- [ ] Verify OTP
- [ ] Submit KYC application
- [ ] Login as admin
- [ ] Review KYC application
- [ ] Download KYC documents
- [ ] Approve/reject KYC
- [ ] Check status update notification

### Unit Tests
- [✅] Password hashing and verification
- [✅] JWT token creation and validation
- [✅] Token refresh mechanism
- [✅] OTP generation
- [✅] Verification token generation

---

## 🐛 Troubleshooting

### Issue: Email verification not working
**Solution**: Check backend logs for verification token and manually construct URL

### Issue: File upload fails
**Solution**: Check file size (<10MB) and format (PDF/JPG/PNG)

### Issue: JWT token expired
**Solution**: Use refresh token to get new access token

### Issue: KYC documents not downloading
**Solution**: Ensure admin role and valid access token

### Issue: Phone OTP not received
**Solution**: Check backend logs for OTP code (mock service)

---

## 📞 Support

For issues or questions:
1. Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
2. Check frontend logs: `tail -f /var/log/supervisor/frontend.*.log`
3. Review this documentation
4. Check API documentation: `http://localhost:8001/docs`

---

**Implementation Status**: ✅ Complete and Tested
**Last Updated**: November 12, 2025
**Platform Version**: 2.0.0
