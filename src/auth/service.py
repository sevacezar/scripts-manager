"""Authentication service for user management and JWT tokens."""

from datetime import datetime, timedelta, UTC
from typing import Any

from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode: dict[str, Any] = data.copy()
    
    if expires_delta:
        expire: datetime = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except ExpiredSignatureError as e:
        logger.warning("JWT has been expired", error=str(e))
        return None
    except JWTError as e:
        logger.warning("JWT decode error", error=str(e))
        return None


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    """
    Get user by login.
    
    Args:
        db: Database session
        login: User login
        
    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Get user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, login: str, password: str, is_admin: bool = False) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        login: User login
        password: Plain text password
        is_admin: Whether user is admin
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If user with login already exists
    """
    # Check if user already exists
    existing_user = await get_user_by_login(db, login)
    if existing_user:
        raise ValueError(f"User with login '{login}' already exists")
    
    # Create new user
    password_hash: str = get_password_hash(password)
    new_user: User = User(
        login=login,
        password_hash=password_hash,
        is_admin=is_admin,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info("User created", user_id=new_user.id, login=login, is_admin=is_admin)
    
    return new_user


async def authenticate_user(db: AsyncSession, login: str, password: str) -> User | None:
    """
    Authenticate user by login and password.
    
    Args:
        db: Database session
        login: User login
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user: User | None = await get_user_by_login(db, login)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

