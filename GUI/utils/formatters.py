from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime


CURRENCY_SYMBOL = "₱"
DATE_FORMAT = "%Y-%m-%d"


def parse_currency(value):
    if value is None:
        raise ValueError("Amount is required.")

    if isinstance(value, Decimal):
        amount = value
    else:
        text = str(value).strip()

        if not text:
            raise ValueError("Amount is required.")

        text = text.replace(CURRENCY_SYMBOL, "")
        text = text.replace(",", "").strip()

        try:
            amount = Decimal(text)
        except InvalidOperation:
            raise ValueError("Invalid amount.")

    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    return int(
        (amount * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def format_currency(cents):
    if cents is None:
        return f"{CURRENCY_SYMBOL}0.00"

    try:
        amount = Decimal(str(cents)) / Decimal("100")
    except (InvalidOperation, ValueError, TypeError):
        return f"{CURRENCY_SYMBOL}0.00"

    return f"{CURRENCY_SYMBOL}{amount:,.2f}"


def format_decimal(value, decimal_places=2):
    if value is None:
        return f"{0:.{decimal_places}f}"

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return f"{0:.{decimal_places}f}"

    return f"{number:,.{decimal_places}f}"


def format_date(value):
    if value is None:
        return ""

    if isinstance(value, datetime):
        return value.strftime(DATE_FORMAT)

    text = str(value).strip()

    if not text:
        return ""

    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(text, fmt).strftime(DATE_FORMAT)
        except ValueError:
            continue

    return text


def parse_date(value):
    if value is None:
        raise ValueError("Date is required.")

    text = str(value).strip()

    if not text:
        raise ValueError("Date is required.")

    try:
        return datetime.strptime(text, DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Invalid date. Use YYYY-MM-DD.")


def format_id(value):
    if value is None:
        return ""

    return str(value).strip()


def parse_id(value):
    if value is None:
        raise ValueError("ID is required.")

    text = str(value).strip()

    if not text:
        raise ValueError("ID is required.")

    try:
        return int(text)
    except ValueError:
        raise ValueError("Invalid ID.")


def format_percentage(value, decimal_places=2):
    if value is None:
        return f"{0:.{decimal_places}f}%"

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return f"{0:.{decimal_places}f}%"

    return f"{number:.{decimal_places}f}%"