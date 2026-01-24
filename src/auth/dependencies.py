"""FastAPI dependencies for authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.service import decode_access_token, get_user_by_id
from src.database import get_db
from src.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token: str = credentials.credentials
    
    # Decode token
    payload: dict | None = decode_access_token(token)
    
    if payload is None:
        logger.warning("Invalid token", token_prefix=token[:10] if len(token) > 10 else token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id_str: str | None = payload.get("sub")
    
    if user_id_str is None:
        logger.warning("Token missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user information",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = int(user_id_str)
    # Get user from database
    user: User | None = await get_user_by_id(db, user_id)
    
    if user is None:
        logger.warning("User not found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (can be extended with additional checks).
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current active User object
    """
    # Additional checks can be added here (e.g., is_active flag)
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current admin user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current admin User object
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        logger.warning("Admin access denied", user_id=current_user.id, login=current_user.login)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )
    
    return current_user

