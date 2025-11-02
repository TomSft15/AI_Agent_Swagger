from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_current_superuser
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, UserWithKeys, UserLLMKeysUpdate
from app.services.user_service import user_service
from app.core.encryption import encrypt_api_key, decrypt_api_key, mask_api_key

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    # Add flags for API keys
    user_dict = {
        **current_user.__dict__,
        "has_openai_key": bool(current_user.openai_api_key),
        "has_anthropic_key": bool(current_user.anthropic_api_key)
    }
    return user_dict


@router.get("/me/keys", response_model=UserWithKeys)
def read_user_keys(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile with masked API keys.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information with masked keys
    """
    user_dict = {
        **current_user.__dict__,
        "has_openai_key": bool(current_user.openai_api_key),
        "has_anthropic_key": bool(current_user.anthropic_api_key)
    }
    
    # Add masked keys if they exist
    if current_user.openai_api_key:
        decrypted = decrypt_api_key(current_user.openai_api_key)
        user_dict["openai_api_key_masked"] = mask_api_key(decrypted) if decrypted else None
    
    if current_user.anthropic_api_key:
        decrypted = decrypt_api_key(current_user.anthropic_api_key)
        user_dict["anthropic_api_key_masked"] = mask_api_key(decrypted) if decrypted else None
    
    return user_dict


@router.put("/me/llm-keys", response_model=UserSchema)
def update_llm_keys(
    keys_update: UserLLMKeysUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user's LLM API keys.
    
    Args:
        keys_update: API keys to update
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Encrypt and update keys
    if keys_update.openai_api_key is not None:
        if keys_update.openai_api_key.strip():
            current_user.openai_api_key = encrypt_api_key(keys_update.openai_api_key)
        else:
            # Empty string = remove key
            current_user.openai_api_key = None
    
    if keys_update.anthropic_api_key is not None:
        if keys_update.anthropic_api_key.strip():
            current_user.anthropic_api_key = encrypt_api_key(keys_update.anthropic_api_key)
        else:
            # Empty string = remove key
            current_user.anthropic_api_key = None
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # Return with flags
    user_dict = {
        **current_user.__dict__,
        "has_openai_key": bool(current_user.openai_api_key),
        "has_anthropic_key": bool(current_user.anthropic_api_key)
    }
    return user_dict


@router.delete("/me/llm-keys/{provider}", response_model=UserSchema)
def delete_llm_key(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific LLM API key.
    
    Args:
        provider: Provider name (openai or anthropic)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    if provider == "openai":
        current_user.openai_api_key = None
    elif provider == "anthropic":
        current_user.anthropic_api_key = None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {provider}. Use 'openai' or 'anthropic'"
        )
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    user_dict = {
        **current_user.__dict__,
        "has_openai_key": bool(current_user.openai_api_key),
        "has_anthropic_key": bool(current_user.anthropic_api_key)
    }
    return user_dict


@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    Args:
        user_in: Updated user data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Check if email is being changed and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_service.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is being changed and if it's already taken
    if user_in.username and user_in.username != current_user.username:
        existing_user = user_service.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    user = user_service.update(db, user=current_user, user_in=user_in)
    
    user_dict = {
        **user.__dict__,
        "has_openai_key": bool(user.openai_api_key),
        "has_anthropic_key": bool(user.anthropic_api_key)
    }
    return user_dict


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (superuser only).
    
    Args:
        user_id: User ID
        current_user: Current authenticated superuser
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_dict = {
        **user.__dict__,
        "has_openai_key": bool(user.openai_api_key),
        "has_anthropic_key": bool(user.anthropic_api_key)
    }
    return user_dict