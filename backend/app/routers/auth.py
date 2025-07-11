from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..dependencies import create_access_token, get_current_user
from ..models.user import User, UserRole
from ..schemas.user import Token, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

class GoogleToken(BaseModel):
    token: str

# Enhanced token response with user info
class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: dict

def _issue_backend_token(user: User) -> TokenWithUser:
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenWithUser(
        access_token=access_token, 
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value
        }
    )

def _get_or_create_user(idinfo: dict, db: Session, provider: str = "google") -> User:
    ext_id = idinfo["sub"]
    user = db.query(User).filter(User.external_id == ext_id).first()
    if user:
        # Update name if changed
        if user.name != idinfo.get("name", ""):
            user.name = idinfo.get("name", "")
            db.commit()
        return user
    
    # Auto-detect role based on email domain (customize as needed)
    email = idinfo["email"]
    role = UserRole.PROFESSOR if any(domain in email for domain in ["@university.edu", "@college.edu", "@school.edu"]) else UserRole.STUDENT
    
    user_in = UserCreate(
        email=email,
        name=idinfo.get("name", ""),
        role=role.value,
        auth_provider=provider,
        external_id=ext_id,
    )
    user = User(**user_in.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _verify_google_id_token(raw_token: str) -> dict:
    idinfo = id_token.verify_oauth2_token(
        raw_token,
        google_requests.Request(),
        audience=settings.google_client_id,
    )

    if idinfo["iss"] not in {
        "accounts.google.com",
        "https://accounts.google.com",
    }:
        raise ValueError("Invalid issuer")

    return idinfo

@router.post("/google", response_model=TokenWithUser, status_code=status.HTTP_200_OK)
async def google_token_login(payload: GoogleToken, db: Session = Depends(get_db)):
    try:
        idinfo = _verify_google_id_token(payload.token)
        user = _get_or_create_user(idinfo, db)
        return _issue_backend_token(user)
    except Exception as e:
        print(f"Auth error: {e}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role.value
    }