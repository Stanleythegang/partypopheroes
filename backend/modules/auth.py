from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import logging

from models.user import UserCreate, UserInDB, UserResponse, Token, RefreshTokenDB
from utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    generate_otp
)
from utils.mock_services import email_service, sms_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Database instance will be injected
db = None

def set_db(database):
    global db
    db = database

# Request/Response models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyEmailRequest(BaseModel):
    token: str

class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Helper functions
async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user by email from database"""
    user_data = await db.users.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None

async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Get user by ID from database"""
    user_data = await db.users.find_one({"id": user_id})
    if user_data:
        return UserInDB(**user_data)
    return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Verify user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register a new user
    - Validates email uniqueness
    - Hashes password
    - Sends verification email
    """
    logger.info(f"Registration attempt for: {user_data.email}")
    
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    verification_token = generate_verification_token()
    user = UserInDB(
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        verification_token=verification_token,
        is_active=True
    )
    
    # Save to database
    await db.users.insert_one(user.dict())
    
    # Send verification email
    await email_service.send_verification_email(
        email=user.email,
        token=verification_token,
        full_name=user.full_name
    )
    
    logger.info(f"✅ User registered: {user.email}")
    
    return UserResponse(**user.dict())

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
    """
    Login user with email and password
    - Returns JWT access token and refresh token
    """
    logger.info(f"Login attempt for: {credentials.email}")
    
    # Get user
    user = await get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Store refresh token
    refresh_token_db = RefreshTokenDB(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    await db.refresh_tokens.insert_one(refresh_token_db.dict())
    
    logger.info(f"✅ User logged in: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email with token
    """
    logger.info(f"Email verification attempt with token: {request.token[:10]}...")
    
    # Find user with verification token
    user_data = await db.users.find_one({"verification_token": request.token})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = UserInDB(**user_data)
    
    # Update user
    await db.users.update_one(
        {"id": user.id},
        {"$set": {
            "is_verified": True,
            "verification_token": None,
            "updated_at": datetime.utcnow()
        }}
    )
    
    logger.info(f"✅ Email verified for: {user.email}")
    
    return {"message": "Email verified successfully"}

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    Send OTP to phone number for verification
    """
    logger.info(f"OTP request for phone: {request.phone}")
    
    # Generate OTP
    otp = generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=10)
    
    # Update user with OTP
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "phone": request.phone,
            "phone_otp": otp,
            "phone_otp_expires": otp_expires,
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Send OTP via SMS
    await sms_service.send_otp(phone=request.phone, otp=otp)
    
    logger.info(f"✅ OTP sent to: {request.phone}")
    
    return {"message": "OTP sent successfully", "expires_in_minutes": 10}

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    Verify phone OTP
    """
    logger.info(f"OTP verification for phone: {request.phone}")
    
    # Get updated user data
    user_data = await db.users.find_one({"id": current_user.id})
    user = UserInDB(**user_data)
    
    # Check OTP
    if not user.phone_otp or user.phone_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Check expiration
    if user.phone_otp_expires and datetime.utcnow() > user.phone_otp_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired"
        )
    
    # Check phone matches
    if user.phone != request.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number mismatch"
        )
    
    # Update user
    await db.users.update_one(
        {"id": user.id},
        {"$set": {
            "phone_verified": True,
            "phone_otp": None,
            "phone_otp_expires": None,
            "updated_at": datetime.utcnow()
        }}
    )
    
    logger.info(f"✅ Phone verified for: {user.email}")
    
    return {"message": "Phone verified successfully"}

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    # Decode refresh token
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Check if refresh token exists and is not revoked
    token_data = await db.refresh_tokens.find_one({
        "token": request.refresh_token,
        "user_id": user_id,
        "is_revoked": False
    })
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token"
        )
    
    refresh_token_db = RefreshTokenDB(**token_data)
    
    # Check expiration
    if datetime.utcnow() > refresh_token_db.expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.id, "email": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Revoke old refresh token
    await db.refresh_tokens.update_one(
        {"id": refresh_token_db.id},
        {"$set": {"is_revoked": True}}
    )
    
    # Store new refresh token
    new_refresh_token_db = RefreshTokenDB(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    await db.refresh_tokens.insert_one(new_refresh_token_db.dict())
    
    logger.info(f"✅ Token refreshed for user: {user.email}")
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

@router.post("/logout")
async def logout(request: RefreshTokenRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    Logout user by revoking refresh token
    """
    # Revoke refresh token
    await db.refresh_tokens.update_many(
        {"token": request.refresh_token, "user_id": current_user.id},
        {"$set": {"is_revoked": True}}
    )
    
    logger.info(f"✅ User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(**current_user.dict())

@router.put("/me", response_model=UserResponse)
async def update_profile(full_name: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    """
    Update user profile
    """
    update_data = {"updated_at": datetime.utcnow()}
    if full_name:
        update_data["full_name"] = full_name
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user_data = await db.users.find_one({"id": current_user.id})
    updated_user = UserInDB(**updated_user_data)
    
    return UserResponse(**updated_user.dict())
