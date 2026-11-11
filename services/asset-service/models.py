from sqlalchemy import Column, UUID, String, Text, DateTime, func
from extensions import db

import uuid

class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(String(100), nullable=False)
    category = db.Column(String(100), nullable=False)
    location = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    created_at = db.Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now())
    updated_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )