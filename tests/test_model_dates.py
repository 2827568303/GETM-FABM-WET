import sys
from datetime import datetime
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


@pytest.mark.parametrize('value, expected', [
    ('2020-DOY060 12:30:00', datetime(2020, 2, 29, 12, 30)),
    ('2020-366', datetime(2020, 12, 31)),
    ('2021-DOY001', datetime(2021, 1, 1)),
])
def test_ordinal_dates(value, expected):
    from model_dates import parse_ordinal_date
    assert parse_ordinal_date(value) == expected


@pytest.mark.parametrize('value', ['2021-366', '2020-000', '2020-367', '2020-DOY060 25:00'])
def test_invalid_ordinal_dates(value):
    from model_dates import parse_ordinal_date
    assert parse_ordinal_date(value) is None
