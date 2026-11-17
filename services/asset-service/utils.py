from flask import jsonify
from sqlalchemy.exc import IntegrityError, OperationalError

from extensions import db
from models import Asset

REQUIRED_FIELDS = {"name", "category", "location"}
ALL_FIELDS = {"name", "category", "location", "description"}

def validate_asset_payload(data: dict, is_update: bool):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    unknown_fields = list(ALL_FIELDS - set(data.keys()))
    if unknown_fields:
        return None, f"Unknown fields: ({", ".join(unknown_fields)})"

    if not is_update:
        missing_fields = list(REQUIRED_FIELDS - set(data.keys()))
        if len(missing_fields) != 0:
            return None, f"Please pass the mandatory fields: ({", ".join(missing_fields)})"

    if is_update and not data:
        return None, f"Provide at least one property from {list(ALL_FIELDS)} to update asset"

    verified_data = {}
    for property, value in data.items():
        if not isinstance(value, str):
            return None, f"Value for property {property} must be of type String"
        if property in ALL_FIELDS:
            verified_data[property] = value.strip()

    return verified_data, None

def commit_asset(asset):
    db.session.add(asset)
    db.session.commit()
    db.session.refresh(asset)

def database_error_response(error):
    db.session.rollback()

    if isinstance(error, IntegrityError):
        return jsonify({
            "code": "asset_conflict",
            "message": "Asset conflicts with an existing record"
        }), 409

    if isinstance(error, OperationalError):
        return jsonify({
            "code": "database_unavailable",
            "message": "The database service is temporarily unavailable"
        }), 503

    return jsonify({
        "code": "database_error",
        "message": str(error)
    }), 500

def asset_to_dictionary(asset: Asset):
    return {
        "id": str(asset.id),
        "name": asset.name,
        "category": asset.category,
        "location": asset.location,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at
    }
