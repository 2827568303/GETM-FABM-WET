"""The simplified tree must keep every existing workflow and top-level tool."""
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'3DWET/app/templates/index.html').read_text(encoding='utf-8')


class Navigation(HTMLParser):
    def __init__(self):
        super().__init__();self.groups={};self.group=None;self.leaves=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='details' and 'data-workflow' in attrs:
            self.group=attrs['data-workflow'];self.groups[self.group]=[]
        if 'data-page' in attrs:
            self.leaves.append((tag,attrs['data-page'],self.group))
            if self.group:self.groups[self.group].append(attrs['data-page'])
    def handle_endtag(self,tag):
        if tag=='details':self.group=None


def test_three_native_workflows_keep_all_pages_as_keyboard_buttons():
    parser=Navigation();parser.feed(HTML)
    assert set(parser.groups)=={'case-data','configuration','run-review'}
    expected={'dashboard','cases','preprocess','input','gridstudio','modules','ecology','parameters','initial','time',
              'run','system','map','viz2d','viz3d','vheat','timeseries','calibrate','autocal'}
    leaves=[row for row in parser.leaves if row[2] is not None]
    assert {page for _,page,_ in leaves}==expected
    assert len(leaves)==len(expected)
    assert all(tag=='button' for tag,_,_ in leaves)
    assert parser.groups['configuration']==['modules','ecology','parameters','initial','time']


def test_original_top_menus_and_tools_remain_connected():
    menu=HTML.split('role="menubar"')[1].split('role="toolbar"')[0]
    for label,page in [('项目','cases'),('编辑','gridstudio'),('视图','dashboard'),('图层','map'),
                       ('运行','run'),('设置','system'),('帮助','system')]:
        assert f'onclick="navigate(\'{page}\')">{label}</button>' in menu
    assert 'onclick="StudioI18n.openDialog()">语言</button>' in menu
    toolbar=HTML.split('role="toolbar"')[1].split('class="topbar"')[0]
    for page in ('cases','preprocess','gridstudio','run','map','viz2d','viz3d','system'):
        assert f'onclick="navigate(\'{page}\')"' in toolbar


def test_tree_has_a_controlled_narrow_screen_navigation_panel():
    assert 'id="studio-navigation"' in HTML
    assert 'id="studio-nav-toggle"' in HTML
    assert 'aria-controls="studio-navigation"' in HTML
    assert 'workflow_navigation.js' in HTML and 'workflow_navigation.css' in HTML
