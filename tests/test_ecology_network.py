import sys
import os
import subprocess
import threading
from pathlib import Path
from types import SimpleNamespace
from flask import Flask
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))


@pytest.fixture
def network(tmp_path):
    from lake_points_api import register_lake_points_routes
    text = '# retain comments\ninstances:\n  a:\n    model: wet/a\n    parameters:\n      rate: 2.0 # keep\n      active: true\n    coupling:\n      pool: b/state\n  b:\n    model: wet/b\n    initialization:\n      state: 1.0\n  c:\n    model: wet/c\n'
    (tmp_path / 'fabm.yaml').write_text(text)
    ctx = SimpleNamespace(active_case_path=tmp_path, _NC_LOCK=threading.RLock(), _case_in_use=lambda p: False)
    app = Flask(__name__); register_lake_points_routes(app, ctx)
    return app.test_client(), ctx, tmp_path, text


def test_real_edges_and_safe_scalar_update(network):
    client, _, path, original = network
    s = client.get('/api/ecology/network').get_json()
    assert s['edges'] == [{'source': 'b', 'target': 'a', 'port': 'pool', 'reference': 'b/state'}]
    r = client.post('/api/ecology/network', json={**s, 'module': 'a', 'parameters': {'rate': 3.5}, 'coupling': {'pool': 'b/state'}})
    assert r.status_code == 200
    assert '# retain comments' in (path / 'fabm.yaml').read_text()
    assert '# keep' in (path / 'fabm.yaml').read_text()
    assert (Path(r.get_json()['backup']) / 'fabm.yaml').read_text() == original


@pytest.mark.parametrize('extra', [{'parameters': {'rate': float('nan')}}, {'parameters': {'active': 'false'}}, {'coupling': {'pool': 'c/fake'}}, {'coupling': {'unknown': 'b/state'}}])
def test_invalid_network_edit_is_non_destructive(network, extra):
    client, _, path, original = network
    s = client.get('/api/ecology/network').get_json()
    r = client.post('/api/ecology/network', json={**s, 'module': 'a', **extra})
    assert r.status_code == 400
    assert (path / 'fabm.yaml').read_text() == original


def test_network_stale_case_config_and_running_guard(network):
    client, ctx, path, original = network
    s = client.get('/api/ecology/network').get_json()
    ctx._case_in_use = lambda p: True


def test_erkan_reference_network_is_fixed_read_only_and_does_not_switch_active_case(network, monkeypatch):
    client, ctx, active_path, _ = network
    ctx.CASE_DIR = active_path
    example = active_path / 'Erken_real_20200101_24h_stage'
    example.mkdir()
    source_text = '''instances:
  cyanobacteria:
    model: wet/phytoplankton
  cladocerans:
    model: wet/zooplankton
    coupling:
      prey_model1: cyanobacteria
  JuFish:
    model: wet/fish
    coupling:
      PLANprey2: cladocerans
'''
    (example / 'fabm.yaml').write_text(source_text, encoding='utf-8')
    from lake_points_api import case_transactions
    original_recover = case_transactions.recover_pending
    def reject_recovery(path):
        if Path(path).resolve() == example.resolve():
            raise AssertionError('read-only reference must not recover or mutate transactions')
        return original_recover(path)
    monkeypatch.setattr(case_transactions, 'recover_pending', reject_recovery)

    response = client.get('/api/ecology/network?source=erken_reference')

    assert response.status_code == 200, response.get_json()
    result = response.get_json()
    assert result['case_path'] == str(example.resolve())
    assert result['edges'] == [
        {'source': 'cyanobacteria', 'target': 'cladocerans', 'port': 'prey_model1', 'reference': 'cyanobacteria'},
        {'source': 'cladocerans', 'target': 'JuFish', 'port': 'PLANprey2', 'reference': 'cladocerans'},
    ]
    assert ctx.active_case_path == active_path
    assert (example / 'fabm.yaml').read_text(encoding='utf-8') == source_text
    assert client.post('/api/ecology/network?source=erken_reference', json={}).status_code == 405


def test_erkan_reference_network_fails_closed_when_fixed_case_is_missing(network):
    client, ctx, active_path, _ = network
    ctx.CASE_DIR = active_path
    response = client.get('/api/ecology/network?source=erken_reference')
    assert response.status_code == 404
    assert ctx.active_case_path == active_path


def test_clone_ui_keeps_copy_default_and_requires_review_of_split_preview():
    root = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
    html = (root / 'templates' / 'index.html').read_text(encoding='utf-8')
    script = (root / 'static' / 'js' / 'ecology_network.js').read_text(encoding='utf-8')
    assert 'ecology_network.js?v=34' in html
    assert '本案例为结构四边形网格' in html
    assert '不是求解器原生三角拓扑' in html
    assert '<option value="continuous" selected>\u8fde\u7eed\u66f2\u9762</option>' in html
    assert '<option value="triangles">\u4e09\u89d2\u7f51\u683c\uff08\u663e\u793a\u5256\u5206\uff09</option>' in html
    assert '\u8fde\u7eed\u66f2\u9762\u53ef\u4f5c\u4e3a\u5927\u578b\u7f51\u683c\u6216\u64ad\u653e\u573a\u666f\u7684\u8f7b\u91cf\u66ff\u4ee3' in html
    assert 'value="copy">完整复制（默认）' in script
    assert 'value="split">同功能群等总量分摊' in script
    assert 'window.confirm(summary)' in script
    assert 'split.states.join' in script
    assert '不是物种/性状差异或竞争结论' in script
def test_edited_strings_are_readable_by_actual_native_yaml_parser(network, tmp_path):
    client, _, path, original = network
    original = original.replace('    model: wet/a', '    long_name: Original name\n    model: wet/a')
    (path / 'fabm.yaml').write_text(original, encoding='utf-8')
    state = client.get('/api/ecology/network').get_json()
    response = client.post('/api/ecology/network', json={**state, 'module':'a',
                           'long_name':'POM test 名称', 'coupling':{'pool':'b/state'}})
    assert response.status_code == 200, response.get_json()
    root = Path(__file__).resolve().parents[1]
    compiler = root / 'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.is_file(): pytest.skip('Portable native Fortran compiler is unavailable')
    program = tmp_path / 'parse_probe.f90'
    program.write_text('''program probe
use yaml, only: parse, error_length
use yaml_types, only: type_node
implicit none
character(2048) :: filename
character(error_length) :: error
class(type_node),pointer :: node
call get_command_argument(1,filename)
node=>parse(trim(filename),13,error)
if(len_trim(error)>0)then
 print *, trim(error)
 stop 1
endif
if(.not.associated(node))stop 2
print *, 'NATIVE YAML PASS'
end program
''', encoding='utf-8')
    executable = tmp_path / 'parse_probe.exe'
    env = dict(os.environ, PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    sources = root / '3DWET/src/fabm/src/yaml'
    compiled = subprocess.run([str(compiler), '-ffree-line-length-none',
                               str(sources/'yaml_types.F90'), str(sources/'yaml.F90'),
                               str(program), '-o', str(executable)], cwd=tmp_path, env=env,
                              capture_output=True, text=True)
    assert compiled.returncode == 0, compiled.stdout+compiled.stderr
    result = subprocess.run([str(executable),str(path/'fabm.yaml')], cwd=tmp_path,env=env,
                            capture_output=True,text=True,timeout=10)
    assert result.returncode == 0, result.stdout+result.stderr
    assert 'NATIVE YAML PASS' in result.stdout


@pytest.mark.parametrize('name', ['bad\nname', 'bad "name"', "bad 'name'", 'bad [name]',
                                 'bad {name}', 'bad # comment', 'bad: mapping', 'true'])
def test_native_unsupported_labels_are_rejected_before_write(network, name):
    client, _, path, original = network
    original = original.replace('    model: wet/a', '    long_name: Original name\n    model: wet/a')
    (path/'fabm.yaml').write_text(original,encoding='utf-8')
    state = client.get('/api/ecology/network').get_json()
    response = client.post('/api/ecology/network',json={**state,'module':'a','long_name':name})
    assert response.status_code == 400
    assert (path/'fabm.yaml').read_text(encoding='utf-8') == original


def test_network_preserves_small_numeric_parameter_type(network):
    client, _, path, _ = network
    state = client.get('/api/ecology/network').get_json()
    response = client.post('/api/ecology/network',json={**state,'module':'a','parameters':{'rate':1e-6}})
    assert response.status_code == 200, response.get_json()
    import yaml
    assert yaml.safe_load((path/'fabm.yaml').read_text())['instances']['a']['parameters']['rate'] == 1e-6
