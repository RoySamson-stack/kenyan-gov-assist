"""
Authentication and security middleware for Kenyan Gov Assist API
"""
import os
import hashlib
import secrets
from typing import Optional, Dict
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Bearer token scheme
BEARER_SCHEME = HTTPBearer()


class AuthService:
    """Handle API authentication and authorization."""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load valid API keys from environment."""
        keys = {}
        
        # Master API key
        master_key = os.getenv("MASTER_API_KEY")
        if master_key:
            keys["master"] = master_key
        
        # Load additional keys from comma-separated env var
        additional_keys = os.getenv("API_KEYS", "")
        if additional_keys:
            for key in additional_keys.split(","):
                if key.strip():
                    keys[f"key_{len(keys)}"] = key.strip()
        
        # If no keys configured, generate a warning
        if not keys and self.require_auth:
            print("WARNING: No API keys configured but auth is required!")
        
        return keys
    
    def verify_api_key(self, api_key: Optional[str] = Security(API_KEY_HEADER)) -> Optional[str]:
        """
        Verify API key from header.
        Returns the key identity if valid, None if auth disabled.
        """
        # If auth not required, allow all requests
        if not self.require_auth:
            return "auth_disabled"
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key. Provide X-API-Key header.",
            )
        
        # Check if key is valid
        for identity, key in self.api_keys.items():
            if secrets.compare_digest(api_key, key):
                return identity
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    
    def verify_bearer_token(self, token: Optional[str] = Depends(BEARER_SCHEME)) -> Optional[str]:
        """
        Verify Bearer token (for OAuth/JWT in future).
        """
        if not self.require_auth:
            return "auth_disabled"
        
        if not token or not token.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        
        # TODO: Implement JWT verification here
        # For now, just check against API keys
        return self.verify_api_key(token.credentials)
    
    def generate_api_key(self, prefix: str = "kg") -> str:
        """Generate a new API key."""
        random_bytes = secrets.token_bytes(32)
        key_hash = hashlib.sha256(random_bytes).hexdigest()
        return f"{prefix}_{key_hash}"


# Global auth service instance
auth_service = AuthService()


def get_current_identity(identity: str = Depends(auth_service.verify_api_key)) -> str:
    """Dependency for getting current authenticated identity."""
    return identity


def require_auth(identity: str = Depends(get_current_identity)) -> str:
    """Dependency that requires authentication."""
    if identity == "auth_disabled":
        return "anonymous"
    return identity
