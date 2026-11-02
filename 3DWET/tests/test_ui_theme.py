from pathlib import Path


CSS = Path(__file__).resolve().parents[1] / 'app' / 'static' / 'css' / 'studio.css'


def test_lake_workbench_theme_contract():
    text = CSS.read_text(encoding='utf-8')
    for token in (
        '--surface-elevated', '--accent-deep', '--shadow-card',
        '.sidebar{', '.nav-item.active::before', '.topbar',
        '.workflow-strip', '.stat-card::before', 'button:focus-visible',
        '#run-log', '.vc-graphic-host', '@media(max-width:760px)',
    ):
        assert token in text, token


def test_theme_keeps_existing_stable_hooks_out_of_css_replacement():
    text = CSS.read_text(encoding='utf-8')
    assert '.nav-item.active' in text
    assert '#run-status-display' in text
    assert '#run-check-panel' in text


def test_qgis_workbench_theme_contract():
    text = CSS.read_text(encoding='utf-8')
    for token in (
        '--qgis-canvas', '--qgis-green', '.qgis-menu-bar',
        '.qgis-tool-bar', '.qgis-tool-btn', '.qgis-status-bar',
        '.qgis-status-item', '.qgis-tool-separator',
    ):
        assert token in text, token

    html = CSS.parent.parent.parent / 'templates' / 'index.html'
    markup = html.read_text(encoding='utf-8')
    for hook in ('qgis-menu-bar', 'qgis-tool-bar', 'qgis-status-bar', 'qgis-status-case', 'qgis-status-run'):
        assert hook in markup, hook
