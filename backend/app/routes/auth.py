from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token, PasswordResetRequest
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user
from app.services.supabase_service import supabase_service
from typing import Any

logger = logging.getLogger("nutriguide.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    clean_email = user_in.email.strip().lower()
    clean_name = user_in.name.strip()
    logger.info(f"Incoming registration request for: '{clean_email}'")

    # Check if email is already taken (case-insensitive)
    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        logger.warning(f"Registration rejected: User with email '{clean_email}' already exists in database.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists. Please log in or use a different email.",
        )
    
    # Hash password and create record
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        name=clean_name,
        email=clean_email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User successfully registered: ID={db_user.id}, email='{clean_email}'")

    # Sync registration to Supabase Cloud Table
    try:
        supabase_service.sync_user_registration({
            "name": db_user.name,
            "email": db_user.email,
            "password_hash": db_user.password_hash,
            "calorie_goal": db_user.calorie_goal,
            "protein_goal": db_user.protein_goal,
            "carbs_goal": db_user.carbs_goal,
            "fat_goal": db_user.fat_goal,
            "fiber_goal": db_user.fiber_goal,
        })
    except Exception as exc:
        logger.warning(f"Supabase REST sync attempt skipped: {exc}")

    return db_user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    clean_email = user_in.email.strip().lower()
    logger.info(f"Incoming login request for: '{clean_email}'")
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        logger.warning(f"Login failed: No account found with email '{clean_email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or account not found. Please register or check your email address.",
        )
    if not verify_password(user_in.password, user.password_hash):
        logger.warning(f"Login failed: Incorrect password provided for email '{clean_email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. The password you entered is wrong. Please try again.",
        )
    
    logger.info(f"Login successful for: '{clean_email}' (User ID: {user.id})")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


# Support standard OAuth2 OAuth2PasswordRequestForm for FastAPI Swagger UI login compatibility
@router.post("/oauth2-login", response_model=Token, include_in_schema=False)
def oauth2_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or account not found.",
        )
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. The password you entered is wrong. Please try again.",
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


@router.post("/reset-password")
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)) -> Any:
    clean_email = data.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found with email '{clean_email}'. Please register a new account.",
        )
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    logger.info(f"Password reset successfully for email: '{clean_email}'")
    return {"message": "Password updated successfully! You can now log in with your new password."}
