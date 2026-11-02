"""Ordinal-day interchange for the UI; native/CF timestamps remain calendar ISO."""
import calendar
from datetime import datetime, timedelta
import re


def parse_calendar_date(value):
    # Python 3.10 only accepts 3 or 6 fractional digits and needs an explicit
    # UTC offset instead of Z. CF labels may trim any trailing zeros.
    text = re.sub(r'(?<=:\d{2})\.(\d{1,6})(?=Z|[+-]\d{2}:?\d{2}|$)',
                  lambda m: '.' + m[1].ljust(6, '0'), str(value).strip())
    return datetime.fromisoformat(text[:-1] + '+00:00' if text.endswith('Z') else text)


def parse_ordinal_date(value):
    match = re.fullmatch(r'(\d{4})-(?:DOY)?(\d{3})([ T].*)?',
                         str(value).strip(), re.IGNORECASE)
    if not match:
        return None
    year, day = int(match[1]), int(match[2])
    if not 1 <= year <= 9999 or not 1 <= day <= 365 + calendar.isleap(year):
        return None
    try:
        date = datetime(year, 1, 1) + timedelta(days=day - 1)
        text = date.strftime('%Y-%m-%d') + (match[3] or '')
        return parse_calendar_date(text)
    except ValueError:
        return None


def format_model_time(value):
    """Serialize Python/CF model clocks without discarding their microseconds."""
    if not hasattr(value, 'strftime'):
        return str(value)
    fraction = getattr(value, 'microsecond', 0)
    return value.strftime('%Y-%m-%d %H:%M:%S') + (f'.{fraction:06d}'.rstrip('0') if fraction else '')
