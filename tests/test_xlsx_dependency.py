"""The supported observation format must work in the application environment."""
import ast
import io
import os
import tempfile
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('header', [['time', 'value', 'variable'], ['unexpected']])
def test_supported_xlsx_observation_is_readable(monkeypatch, header):
    source = ROOT / '3DWET/app/server.py'
    names = {'_parse_xlsx_calibration', '_normalize_calib_column'}
    nodes = [n for n in ast.parse(source.read_text(encoding='utf-8')).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    scope = {'tempfile': tempfile, 'Path': Path, 'os': os}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), scope)
    from openpyxl import Workbook
    book = Workbook()
    book.active.append(header)
    book.active.append(['2020-01-01 00:00:00', 12.5, 'temp'])
    data = io.BytesIO()
    book.save(data)
    data.seek(0)
    temporary_paths = []
    original_factory = tempfile.NamedTemporaryFile
    def tracked_temp(*a, **kw):
        file = original_factory(*a, **kw)
        temporary_paths.append(Path(file.name))
        return file
    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', tracked_temp)
    if header == ['unexpected']:
        with pytest.raises(ValueError, match='time.*value'):
            scope['_parse_xlsx_calibration'](data)
    else:
        rows = scope['_parse_xlsx_calibration'](data)
        assert rows == [{'time': '2020-01-01 00:00:00', 'value': 12.5, 'variable': 'temp'}]
    assert temporary_paths and not any(p.exists() for p in temporary_paths)


def test_xlsx_is_an_explicit_install_dependency():
    requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8').lower()
    assert any(line.startswith('openpyxl') for line in requirements.splitlines())
