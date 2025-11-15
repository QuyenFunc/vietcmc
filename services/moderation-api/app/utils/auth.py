import hmac
import hashlib
import secrets
import uuid
from typing import Tuple


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"sk_live_{secrets.token_urlsafe(32)}"


def generate_hmac_secret() -> str:
    """Generate a secure HMAC secret"""
    return f"whsec_{secrets.token_urlsafe(32)}"


def generate_app_id() -> str:
    """Generate a unique app ID"""
    return str(uuid.uuid4())


def generate_credentials() -> Tuple[str, str, str]:
    """Generate app_id, api_key, and hmac_secret"""
    return (
        generate_app_id(),
        generate_api_key(),
        generate_hmac_secret()
    )


def verify_hmac_signature(secret: str, body: bytes, signature: str) -> bool:
    """
    Verify HMAC-SHA256 signature
    
    Args:
        secret: HMAC secret key
        body: Request body as bytes
        signature: Signature header value (format: "sha256=<hex>")
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not signature.startswith('sha256='):
        return False
    
    # Remove 'sha256=' prefix
    received_signature = signature[7:]
    
    # Compute expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(received_signature, expected_signature)


def generate_hmac_signature(secret: str, body: bytes) -> str:
    """
    Generate HMAC-SHA256 signature
    
    Args:
        secret: HMAC secret key
        body: Request body as bytes
    
    Returns:
        Signature in format "sha256=<hex>"
    """
    signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return f"sha256={signature}"

