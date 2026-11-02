from pathlib import Path
from datetime import datetime, timezone
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from observations import parse_observations


def test_ordinal_observation_dates_preview_with_source_clock_and_invalid_day(tmp_path):
    source = tmp_path / 'observations.csv'
    source.write_text(
        'time,value,unit,variable\n'
        '2020-DOY060 12:30:00+08:00,4,degC,temp\n'
        '2021-DOY366,5,degC,temp\n', encoding='utf-8')
    result = parse_observations(source)
    assert len(result['records']) == 1
    assert result['records'][0]['time'] == '2020-02-29 12:30:00+08:00'
    assert result['records'][0]['time_basis'] == 'source_offset'
    assert datetime.fromisoformat(result['records'][0]['time']).astimezone(timezone.utc).isoformat() == '2020-02-29T04:30:00+00:00'
    assert [(d['source_line'], d['reason']) for d in result['diagnostics']] == [(3, 'invalid_time')]
