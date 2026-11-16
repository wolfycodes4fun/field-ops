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
        else:
            verified_data[property] = value.strip()

    return verified_data, None