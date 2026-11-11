from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, UUID, String, Text, DateTime, func
import uuid

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"

    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )