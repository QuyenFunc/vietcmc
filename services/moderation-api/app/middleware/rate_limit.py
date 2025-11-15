from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


limiter = Limiter(key_func=get_remote_address)


def get_client_id(request: Request) -> str:
    """Get client ID from request for rate limiting"""
    # Try to get from authenticated client
    if hasattr(request.state, 'client'):
        return f"client_{request.state.client.id}"
    
    # Fallback to IP address
    return get_remote_address(request)

