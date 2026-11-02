import sys
import time
from pathlib import Path

from jinja2 import FileSystemLoader

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
import server


def test_index_template_is_reloaded_when_source_changes(tmp_path, monkeypatch):
    template_path = tmp_path / "index.html"
    template_path.write_text("template-v1", encoding="utf-8")
    monkeypatch.setattr(server.app.jinja_env, "loader", FileSystemLoader(str(tmp_path)))
    server.app.jinja_env.cache.clear()

    client = server.app.test_client()
    assert client.get("/").get_data(as_text=True) == "template-v1"

    template_path.write_text("template-v2", encoding="utf-8")
    time.sleep(1.1)  # Ensure the file mtime differs on filesystems with 1s resolution.

    assert client.get("/").get_data(as_text=True) == "template-v2"
