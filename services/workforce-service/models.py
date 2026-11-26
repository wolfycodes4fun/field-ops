from sqlalchemy import (
    CheckConstraint,
    Uuid,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    )

import uuid

from extensions import db

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('administrator', 'manager', 'technician')",
            name="check_user_roles"
        ),
    )

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(String(length=256), nullable=False, unique=True)
    display_name = db.Column(String(length=128), nullable=False, unique=True)
    password_hash = db.Column(String(length=64), nullable=False)
    role = db.Column(String(length=15), nullable=False)
    is_active = db.Column(Boolean, nullable=False, default=True)
    created_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

class StaffProfile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    full_name = db.Column(String(length=256), nullable=False)
    job_title = db.Column(String(length=64), nullable=False)
    team = db.Column(String(length=64))
    phone = db.Column(String(length=32))
    employee_number = db.Column(String(length=128), nullable=False, unique=True)
    created_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
