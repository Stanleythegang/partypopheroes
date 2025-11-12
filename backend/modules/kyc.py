from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
import logging
import os
from pathlib import Path
import io

from models.kyc import (
    KYCApplicationCreate,
    KYCApplicationInDB,
    KYCApplicationResponse,
    KYCDocument,
    KYCReviewAction
)
from models.user import UserInDB
from modules.auth import get_current_user, get_admin_user
from utils.security import encrypt_file, decrypt_file, hash_filename
from utils.mock_services import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kyc", tags=["KYC"])

# Storage directory for encrypted files
STORAGE_DIR = Path("/app/backend/storage/kyc")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Database instance
db = None

def set_db(database):
    global db
    db = database

# Helper functions
async def save_encrypted_file(file: UploadFile, user_id: str) -> KYCDocument:
    """Save and encrypt uploaded file"""
    # Read file data
    file_data = await file.read()
    file_size = len(file_data)
    
    # Encrypt file
    encrypted_data = encrypt_file(file_data)
    
    # Generate secure filename
    secure_filename = hash_filename(file.filename, user_id)
    file_path = STORAGE_DIR / secure_filename
    
    # Save encrypted file
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    logger.info(f"📁 File saved and encrypted: {secure_filename}")
    
    return KYCDocument(
        filename=secure_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        encrypted=True
    )

async def get_kyc_application(kyc_id: str) -> Optional[KYCApplicationInDB]:
    """Get KYC application by ID"""
    kyc_data = await db.kyc_applications.find_one({"id": kyc_id})
    if kyc_data:
        return KYCApplicationInDB(**kyc_data)
    return None

async def get_user_kyc(user_id: str) -> Optional[KYCApplicationInDB]:
    """Get user's KYC application"""
    kyc_data = await db.kyc_applications.find_one({"user_id": user_id})
    if kyc_data:
        return KYCApplicationInDB(**kyc_data)
    return None

# Endpoints
@router.post("/apply", response_model=KYCApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_kyc_application(
    business_name: str = Form(...),
    business_type: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    country: str = Form(...),
    postal_code: str = Form(...),
    tax_id: Optional[str] = Form(None),
    id_document: UploadFile = File(...),
    business_document: UploadFile = File(...),
    additional_documents: List[UploadFile] = File(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Submit KYC application with documents
    - Uploads and encrypts ID document
    - Uploads and encrypts business document
    - Optional additional documents
    """
    logger.info(f"KYC application submission from user: {current_user.email}")
    
    # Check if user already has a KYC application
    existing_kyc = await get_user_kyc(current_user.id)
    if existing_kyc and existing_kyc.status != "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"KYC application already exists with status: {existing_kyc.status}"
        )
    
    # Validate file types (basic validation)
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    
    def validate_file(file: UploadFile):
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {ext}. Allowed: {', '.join(allowed_extensions)}"
            )
    
    validate_file(id_document)
    validate_file(business_document)
    
    # Save and encrypt documents
    id_doc = await save_encrypted_file(id_document, current_user.id)
    business_doc = await save_encrypted_file(business_document, current_user.id)
    
    # Handle additional documents
    additional_docs = []
    if additional_documents:
        for doc in additional_documents:
            if doc.filename:  # Check if file was actually uploaded
                validate_file(doc)
                additional_doc = await save_encrypted_file(doc, current_user.id)
                additional_docs.append(additional_doc)
    
    # Create KYC application
    kyc_application = KYCApplicationInDB(
        user_id=current_user.id,
        business_name=business_name,
        business_type=business_type,
        tax_id=tax_id,
        address=address,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code,
        id_document=id_doc,
        business_document=business_doc,
        additional_documents=additional_docs,
        status="pending"
    )
    
    # Save to database
    await db.kyc_applications.insert_one(kyc_application.dict())
    
    # Update user role to seller (pending verification)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"role": "seller", "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"✅ KYC application submitted: {kyc_application.id}")
    
    return KYCApplicationResponse(**kyc_application.dict())

@router.get("/my-application", response_model=KYCApplicationResponse)
async def get_my_kyc(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's KYC application"""
    kyc = await get_user_kyc(current_user.id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No KYC application found"
        )
    
    return KYCApplicationResponse(**kyc.dict())

@router.get("/applications", response_model=List[KYCApplicationResponse])
async def list_kyc_applications(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """
    List all KYC applications (Admin only)
    - Filter by status (pending, approved, rejected, under_review)
    """
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    applications = await db.kyc_applications.find(query).skip(skip).limit(limit).to_list(limit)
    
    return [KYCApplicationResponse(**app) for app in applications]

@router.get("/applications/{kyc_id}", response_model=KYCApplicationResponse)
async def get_kyc_application_details(
    kyc_id: str,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """Get KYC application details (Admin only)"""
    kyc = await get_kyc_application(kyc_id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC application not found"
        )
    
    return KYCApplicationResponse(**kyc.dict())

@router.get("/download/{kyc_id}/{document_type}")
async def download_kyc_document(
    kyc_id: str,
    document_type: str,  # id_document, business_document, additional_{index}
    admin_user: UserInDB = Depends(get_admin_user)
):
    """
    Download and decrypt KYC document (Admin only)
    """
    kyc = await get_kyc_application(kyc_id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC application not found"
        )
    
    # Get document based on type
    document = None
    if document_type == "id_document":
        document = kyc.id_document
    elif document_type == "business_document":
        document = kyc.business_document
    elif document_type.startswith("additional_"):
        try:
            index = int(document_type.split("_")[1])
            if index < len(kyc.additional_documents):
                document = kyc.additional_documents[index]
        except (ValueError, IndexError):
            pass
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Read encrypted file
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Decrypt file
    decrypted_data = decrypt_file(encrypted_data)
    
    logger.info(f"📥 Document downloaded: {document.original_filename} by admin {admin_user.email}")
    
    # Return file as streaming response
    return StreamingResponse(
        io.BytesIO(decrypted_data),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={document.original_filename}"
        }
    )

@router.post("/review/{kyc_id}")
async def review_kyc_application(
    kyc_id: str,
    review: KYCReviewAction,
    admin_user: UserInDB = Depends(get_admin_user)
):
    """
    Review KYC application - approve or reject (Admin only)
    """
    logger.info(f"KYC review for {kyc_id} by admin {admin_user.email}: {review.action}")
    
    kyc = await get_kyc_application(kyc_id)
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC application not found"
        )
    
    # Validate action
    if review.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'approve' or 'reject'"
        )
    
    # Update KYC status
    new_status = "approved" if review.action == "approve" else "rejected"
    
    update_data = {
        "status": new_status,
        "reviewed_at": datetime.utcnow(),
        "reviewed_by": admin_user.id,
        "review_notes": review.notes
    }
    
    if review.action == "reject" and review.rejection_reason:
        update_data["rejection_reason"] = review.rejection_reason
    
    await db.kyc_applications.update_one(
        {"id": kyc_id},
        {"$set": update_data}
    )
    
    # Get user and send notification
    user_data = await db.users.find_one({"id": kyc.user_id})
    if user_data:
        user = UserInDB(**user_data)
        await email_service.send_kyc_status_email(
            email=user.email,
            status=new_status,
            full_name=user.full_name,
            notes=review.notes or review.rejection_reason
        )
    
    logger.info(f"✅ KYC {new_status}: {kyc_id}")
    
    return {
        "message": f"KYC application {new_status}",
        "kyc_id": kyc_id,
        "status": new_status
    }

@router.get("/stats")
async def get_kyc_stats(admin_user: UserInDB = Depends(get_admin_user)):
    """Get KYC statistics (Admin only)"""
    
    total = await db.kyc_applications.count_documents({})
    pending = await db.kyc_applications.count_documents({"status": "pending"})
    approved = await db.kyc_applications.count_documents({"status": "approved"})
    rejected = await db.kyc_applications.count_documents({"status": "rejected"})
    under_review = await db.kyc_applications.count_documents({"status": "under_review"})
    
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "under_review": under_review
    }
