"""Bearer token authentication middleware."""
import os
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def get_bearer_token() -> str:
    """Get the expected bearer token from environment."""
    token = os.environ.get("MCP_BEARER_TOKEN")
    if not token:
        raise RuntimeError("MCP_BEARER_TOKEN environment variable is not set")
    return token


async def verify_token(credentials: HTTPAuthorizationCredentials) -> str:
    """Verify the bearer token from the Authorization header."""
    expected_token = get_bearer_token()
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
