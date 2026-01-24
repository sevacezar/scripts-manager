"""Database models for scripts and folders management."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.auth.models import User


class Folder(Base):
    """Folder model for organizing scripts."""

    __tablename__ = "folders"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    path: str = Column(String, unique=True, index=True, nullable=False)
    parent_id: int | None = Column(
        Integer,
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_by_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    # Relationships
    parent: Mapped["Folder | None"] = relationship(
        "Folder",
        remote_side=[id],
        backref="subfolders",
    )
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    scripts: Mapped[list["Script"]] = relationship(
        "Script",
        back_populates="folder",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Folder."""
        return f"<Folder(id={self.id}, name='{self.name}', path='{self.path}')>"


class Script(Base):
    """Script model for Python scripts."""

    __tablename__ = "scripts"

    id: int = Column(Integer, primary_key=True, index=True)
    filename: str = Column(String, nullable=False)  # Original filename for display
    storage_filename: str = Column(String, nullable=False, index=True)  # Physical filename in scripts/ directory
    logical_path: str = Column(String, unique=True, index=True, nullable=False)  # Logical path for execution (e.g., "geology/test.py")
    display_name: str = Column(String, nullable=False)
    description: str | None = Column(Text, nullable=True)
    folder_id: int | None = Column(
        Integer,
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_by_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    # Relationships
    folder: Mapped["Folder | None"] = relationship("Folder", back_populates="scripts")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        """String representation of Script."""
        return f"<Script(id={self.id}, filename='{self.filename}', logical_path='{self.logical_path}')>"

