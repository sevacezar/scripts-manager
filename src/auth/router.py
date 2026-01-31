"""Router for authentication endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.models import User
from src.auth.schemas import (
    OnboardingStatusUpdate,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from src.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_onboarding_status,
)
from src.config import settings
from src.database import get_db
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account.",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        user: User = await create_user(
            db=db,
            login=user_data.login,
            password=user_data.password,
            is_admin=False,
        )
        
        logger.info("User registered", user_id=user.id, login=user.login)
        
        return UserResponse.model_validate(user)
        
    except ValueError as e:
        logger.warning("Registration failed", error=str(e), login=user_data.login)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Registration error", error=str(e), login=user_data.login)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and get access token.",
)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login user and return JWT access token.
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user: User | None = await authenticate_user(
        db=db,
        login=user_data.login,
        password=user_data.password,
    )
    
    if not user:
        logger.warning("Login failed", login=user_data.login)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires: timedelta = timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    access_token: str = create_access_token(
        data={"sub": str(user.id), "login": user.login},
        expires_delta=access_token_expires,
    )
    
    logger.info("User logged in", user_id=user.id, login=user.login)
    
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/logout",
    summary="Logout user",
    description="Logout user (token invalidation handled client-side).",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """
    Logout user.
    
    Note: Since we're using stateless JWT tokens, logout is handled
    client-side by removing the token. This endpoint is provided for
    consistency and can be extended for token blacklisting if needed.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    logger.info("User logged out", user_id=current_user.id, login=current_user.login)
    
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information.",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/onboarding-status",
    response_model=UserResponse,
    summary="Update onboarding status",
    description="Update whether current user needs onboarding.",
)
async def update_onboarding_status_endpoint(
    status_update: OnboardingStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update onboarding status for current user.
    
    Args:
        status_update: Onboarding status update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        updated_user: User = await update_onboarding_status(
            db=db,
            user_id=current_user.id,
            needs_onboarding=status_update.needs_onboarding,
        )
        
        logger.info(
            "Onboarding status updated via API",
            user_id=current_user.id,
            needs_onboarding=status_update.needs_onboarding,
        )
        
        return UserResponse.model_validate(updated_user)
        
    except ValueError as e:
        logger.warning(
            "Onboarding status update failed",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "Onboarding status update error",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус онбординга",
        )

