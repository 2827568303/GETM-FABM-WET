"""Typed parameter changes must not silently change model YAML types."""
import ast
from pathlib import Path
import pytest
import yaml

SOURCE=Path(__file__).resolve().parents[1]/'3DWET/app/server.py'


@pytest.fixture
def editor(tmp_path):
    nodes=[n for n in ast.parse(SOURCE.read_text(encoding='utf-8')).body
           if isinstance(n, ast.FunctionDef) and n.name in ('_fabm_set_value','update_fabm_parameter')]
    scope={'yaml':yaml}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),scope)
    path=tmp_path/'fabm.yaml'
    path.write_text(yaml.safe_dump({'instances':{'m':{'parameters':{'flag':True,'code':'001','rate':1.}}}}))
    return path,scope['update_fabm_parameter']


@pytest.mark.parametrize('key,value',[('flag','false'),('rate',''),('rate',True),('rate',float('nan')),('code',123),('unknown',1)])
def test_wrong_types_never_change_file(editor,key,value):
    path,update=editor; before=path.read_bytes()
    with pytest.raises(ValueError):update(path,'m',key,value)
    assert path.read_bytes()==before


@pytest.mark.parametrize('key,value',[('flag',False),('rate',2),('code',''),('code','00123')])
def test_valid_types_round_trip(editor,key,value):
    path,update=editor
    assert update(path,'m',key,value)
    actual=yaml.safe_load(path.read_text())['instances']['m']['parameters'][key]
    assert actual==value and type(actual) is type(value)
