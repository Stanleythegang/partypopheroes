import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MockEmailService:
    """Mock email service for testing"""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_verification_email(self, email: str, token: str, full_name: str) -> bool:
        """Mock send verification email"""
        verification_link = f"http://localhost:3000/verify-email?token={token}"
        
        email_data = {
            "to": email,
            "subject": "Verify Your Hamro Account",
            "body": f"""
            Hi {full_name},
            
            Welcome to Hamro! Please verify your email address by clicking the link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            """
        }
        
        self.sent_emails.append(email_data)
        logger.info(f"📧 MOCK EMAIL SENT to {email}")
        logger.info(f"🔗 Verification link: {verification_link}")
        logger.info(f"🎫 Token: {token}")
        
        return True
    
    async def send_kyc_status_email(self, email: str, status: str, full_name: str, notes: Optional[str] = None) -> bool:
        """Mock send KYC status update email"""
        email_data = {
            "to": email,
            "subject": f"KYC Application {status.title()}",
            "body": f"""
            Hi {full_name},
            
            Your KYC application has been {status}.
            
            {notes if notes else ''}
            
            Login to your account to see more details.
            """
        }
        
        self.sent_emails.append(email_data)
        logger.info(f"📧 MOCK KYC EMAIL SENT to {email} - Status: {status}")
        
        return True

class MockSMSService:
    """Mock SMS service for testing"""
    
    def __init__(self):
        self.sent_sms = []
    
    async def send_otp(self, phone: str, otp: str) -> bool:
        """Mock send OTP via SMS"""
        sms_data = {
            "to": phone,
            "message": f"Your Hamro verification code is: {otp}. Valid for 10 minutes."
        }
        
        self.sent_sms.append(sms_data)
        logger.info(f"📱 MOCK SMS SENT to {phone}")
        logger.info(f"🔢 OTP: {otp}")
        
        return True

# Global instances
email_service = MockEmailService()
sms_service = MockSMSService()
