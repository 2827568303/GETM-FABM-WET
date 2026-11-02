"""Windows UTF-8 BOM must not silently erase the first model section."""
import ast
from pathlib import Path


def test_windows_bom_preserves_param_on_save(tmp_path):
    source=Path(__file__).resolve().parents[1]/'3DWET/app/server.py'
    nodes=[n for n in ast.parse(source.read_text(encoding='utf-8')).body
           if isinstance(n,ast.FunctionDef) and n.name in ('parse_getm_inp','write_getm_inp')]
    scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),scope)
    inp=tmp_path/'getm.inp'
    inp.write_text("&param\n runtype = 4\n runid = 'TEST'\n/\n&time\n timestep = 2\n/\n",encoding='utf-8-sig')
    config=scope['parse_getm_inp'](inp)
    assert config['param']=={'runtype':4,'runid':'TEST'}
    scope['write_getm_inp'](inp,config)
    assert inp.read_text().startswith('&param\n')
