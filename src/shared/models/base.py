"""
Base model with common fields and utilities
"""
from datetime import datetime

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseSchema(PydanticBase):
    """Base Pydantic schema with common config"""

    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode (SQLAlchemy -> Pydantic)
        populate_by_name=True,
        use_enum_values=True,
    )


__all__ = ["Base", "TimestampMixin", "BaseSchema"]
