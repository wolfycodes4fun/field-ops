from sqlalchemy import (
    CheckConstraint,
    Uuid,
    String,
    Boolean,
    DateTime,
    func,
    )

import uuid

from extensions import db

class Workforce(db.Model):
    __tablename__ = "workforces"
    __tableargs__ = (
        CheckConstraint(
            "role IN ('admin', 'manager', 'technician')",
            name="check_user_roles"
        ),
    )

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(String(length=256), nullable=False, unique=True)
    display_name = db.Column(String(length=128), nullable=False)
    password_hash = db.Column(String(length=256), nullable=False)
    role = db.Column(String(length=15), nullable=False)
    is_active = db.Column(Boolean, nullable=False, default=True)
    created_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
