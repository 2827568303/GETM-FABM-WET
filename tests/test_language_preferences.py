import sys
from pathlib import Path
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from runtime import register_system_routes


def client(root):
    app = Flask(__name__)
    register_system_routes(app, root, 'test')
    return app.test_client()


def test_language_survives_service_restart(tmp_path):
    first = client(tmp_path)
    assert first.get('/api/system/language').json == {'locale': 'zh-CN', 'packs': []}
    saved = {'locale': 'fr-FR', 'packs': [{'locale': 'fr-FR', 'name': 'Français', 'messages': {'取消': 'Annuler'}}]}
    assert first.put('/api/system/language', json=saved).json['saved']
    assert client(tmp_path).get('/api/system/language').json == saved


def test_language_rejects_foreign_origin_and_oversized_payload(tmp_path):
    api = client(tmp_path)
    assert api.put('/api/system/language', json={'locale': 'en-US', 'packs': []}, headers={'Origin': 'http://evil.example'}).status_code == 403
    assert api.put('/api/system/language', data='x' * (2 * 1024 * 1024 + 1), content_type='application/json').status_code == 413
    assert api.put('/api/system/language', json={'path': '../outside'}).status_code == 400
    assert not (tmp_path / '.studio-runtime/language.json').exists()
