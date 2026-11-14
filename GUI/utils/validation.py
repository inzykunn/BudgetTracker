import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def require_text(value, field_name="Field"):
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required.")

    return str(value).strip()


def require_id(value, field_name="ID"):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid ID.")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return value


def validate_currency(value, field_name="Amount", allow_zero=False):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    text = str(value).strip()
    text = text.replace("₱", "").replace(",", "").strip()

    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a valid amount.")

    if amount < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    if not allow_zero and amount == 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return amount


def validate_date(value, field_name="Date"):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    if hasattr(value, "strftime"):
        return value

    text = str(value).strip()

    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.")


def validate_email(value, field_name="Email"):
    value = require_text(value, field_name)

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(pattern, value):
        raise ValueError(f"{field_name} must be a valid email address.")

    return value


def validate_phone(value, field_name="Phone"):
    value = require_text(value, field_name)

    cleaned = re.sub(r"[\s\-()+]", "", value)

    if not cleaned.isdigit():
        raise ValueError(f"{field_name} must contain only valid phone characters.")

    return value


def validate_positive_number(value, field_name="Value", allow_zero=False):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    if not allow_zero and number == 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return number


def validate_choice(value, field_name="Selection"):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    return value


def validate_length(value, field_name="Field", min_length=None, max_length=None):
    value = require_text(value, field_name)

    length = len(value)

    if min_length is not None and length < min_length:
        raise ValueError(
            f"{field_name} must be at least {min_length} characters."
        )

    if max_length is not None and length > max_length:
        raise ValueError(
            f"{field_name} must not exceed {max_length} characters."
        )

    return value


def validate_form(data, rules):
    errors = {}

    for field_name, validators in rules.items():
        value = data.get(field_name)

        if not isinstance(validators, (list, tuple)):
            validators = [validators]

        for validator in validators:
            try:
                data[field_name] = validator(value)
            except ValueError as error:
                errors[field_name] = str(error)
                break

    if errors:
        raise ValueError("\n".join(errors.values()))

    return data