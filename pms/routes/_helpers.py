from datetime import datetime
from ..services import ServiceError


def parse_date(value, field_name):
    if not value:
        raise ServiceError(f"{field_name} is required")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ServiceError(f"{field_name} has invalid format")


def parse_optional_date(value, field_name):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ServiceError(f"{field_name} has invalid format")


def parse_time(value, field_name):
    if not value:
        raise ServiceError(f"{field_name} is required")
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ServiceError(f"{field_name} has invalid format")


def parse_int(value, field_name):
    if value is None or value == "":
        raise ServiceError(f"{field_name} is required")
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ServiceError(f"{field_name} must be a number")
