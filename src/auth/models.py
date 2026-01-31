"""User model for authentication."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from src.database import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    login: str = Column(String, unique=True, index=True, nullable=False)
    password_hash: str = Column(String, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    needs_onboarding: bool = Column(Boolean, default=True, nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, login='{self.login}', is_admin={self.is_admin}, needs_onboarding={self.needs_onboarding})>"

