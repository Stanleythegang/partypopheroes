"""
Unit tests for authentication module
"""
import pytest
from utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    generate_otp
)

def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Should verify correct password
    assert verify_password(password, hashed) == True
    
    # Should not verify incorrect password
    assert verify_password("WrongPassword", hashed) == False

def test_access_token_creation():
    """Test JWT access token creation and decoding"""
    data = {"sub": "user123", "email": "test@example.com"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Should be able to decode
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"

def test_refresh_token_creation():
    """Test JWT refresh token creation"""
    data = {"sub": "user123"}
    token = create_refresh_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Should be able to decode
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"

def test_verification_token_generation():
    """Test verification token generation"""
    token1 = generate_verification_token()
    token2 = generate_verification_token()
    
    # Tokens should be strings
    assert isinstance(token1, str)
    assert isinstance(token2, str)
    
    # Tokens should be unique
    assert token1 != token2
    
    # Tokens should have reasonable length
    assert len(token1) > 20
    assert len(token2) > 20

def test_otp_generation():
    """Test OTP generation"""
    otp1 = generate_otp()
    otp2 = generate_otp()
    
    # OTPs should be strings
    assert isinstance(otp1, str)
    assert isinstance(otp2, str)
    
    # OTPs should be 6 digits
    assert len(otp1) == 6
    assert len(otp2) == 6
    
    # OTPs should be numeric
    assert otp1.isdigit()
    assert otp2.isdigit()

def test_token_decoding_invalid():
    """Test decoding invalid token"""
    invalid_token = "invalid.token.here"
    payload = decode_token(invalid_token)
    
    # Should return None for invalid token
    assert payload is None

if __name__ == "__main__":
    # Run all tests
    test_password_hashing()
    test_access_token_creation()
    test_refresh_token_creation()
    test_verification_token_generation()
    test_otp_generation()
    test_token_decoding_invalid()
    
    print("✅ All authentication security tests passed!")
