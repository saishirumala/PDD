from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user
from typing import Any

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    
    # Hash password and create record
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


# Support standard OAuth2 OAuth2PasswordRequestForm for FastAPI Swagger UI login compatibility
@router.post("/oauth2-login", response_model=Token, include_in_schema=False)
def oauth2_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    # Since JWT is stateless, logout is handled client-side by clearing the token.
    # Return success confirmation.
    return {"detail": "Successfully logged out. Please clear your authentication token."}


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user
