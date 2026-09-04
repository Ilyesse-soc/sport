from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
BEARER_TOKEN_TYPE = "bearer"  # nosec B105 - OAuth2 token type value


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    first_name: str = Field(default="", max_length=80)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


@router.post("/register")
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request, "auth")
    if not get_settings().enable_local_auth:
        raise HTTPException(status_code=404, detail="Local auth disabled")
    email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        id=uuid4(),
        email=email,
        first_name=payload.first_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": BEARER_TOKEN_TYPE, "user_id": str(user.id)}


@router.post("/login")
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> dict:
    enforce_rate_limit(request, "auth")
    if not get_settings().enable_local_auth:
        raise HTTPException(status_code=404, detail="Local auth disabled")
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    hashed = getattr(user, "hashed_password", "")
    if not verify_password(payload.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": BEARER_TOKEN_TYPE, "user_id": str(user.id)}
