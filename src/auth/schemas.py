"""Pydantic schemas for authentication."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""

    login: str = Field(..., min_length=3, max_length=50, description="User login")


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, description="User password")


class UserLogin(BaseModel):
    """Schema for user login."""

    login: str = Field(..., description="User login")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user response."""

    id: int = Field(description="User ID")
    is_admin: bool = Field(description="Is user admin")
    needs_onboarding: bool = Field(description="Whether user needs onboarding")
    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="User last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for token data."""

    user_id: int | None = None
    login: str | None = None


class OnboardingStatusUpdate(BaseModel):
    """Schema for updating onboarding status."""

    needs_onboarding: bool = Field(description="Whether user needs onboarding")

