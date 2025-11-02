"""
Encryption utilities for sensitive data like API keys.
Uses Fernet (symmetric encryption) from cryptography library.
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Generate encryption key from SECRET_KEY.
    
    Returns:
        Fernet-compatible encryption key
    """
    # Use SECRET_KEY to derive a Fernet key
    # Fernet key must be 32 url-safe base64-encoded bytes
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Encrypted API key as string
    """
    if not api_key:
        return None
    
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an API key.
    
    Args:
        encrypted_key: Encrypted API key
        
    Returns:
        Plain text API key
    """
    if not encrypted_key:
        return None
    
    try:
        f = Fernet(get_encryption_key())
        decrypted = f.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception:
        # If decryption fails, return None
        return None


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display (show only last N characters).
    
    Args:
        api_key: Plain text API key
        visible_chars: Number of characters to show at the end
        
    Returns:
        Masked API key (e.g., "sk-...xyz123")
    """
    if not api_key or len(api_key) <= visible_chars:
        return "****"
    
    return f"{api_key[:3]}...{api_key[-visible_chars:]}"