"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class URL(Base):
    """Database model for shortened URLs."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index('idx_short_code', 'short_code'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_active', 'is_active'),
    )

    def __repr__(self):
        return f"<URL(short_code='{self.short_code}', original_url='{self.original_url}')>"
