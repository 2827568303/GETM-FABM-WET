"""All built-in module explanations must have usable English counterparts."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_module_glossary_covers_all_chinese_descriptions():
    docs = json.loads((ROOT/'3DWET/app/fabm_glossary.json').read_text(encoding='utf-8'))
    english = docs.get('modules_en', {})
    assert set(docs['modules']) <= set(english)
    assert all(text.strip() and not any('\u4e00' <= c <= '\u9fff' for c in text)
               for text in english.values())
    tree = ast.parse((ROOT/'3DWET/app/server.py').read_text(encoding='utf-8'))
    categories = next(ast.literal_eval(n.value) for n in tree.body
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MODULE_CATEGORIES' for t in n.targets))
    assert {v['category'] for v in categories.values()} <= set(docs['categories_en'])


def test_module_annotation_preserves_case_original_names():
    source = ROOT/'3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_annotate_module')
    docs = json.loads((ROOT/'3DWET/app/fabm_glossary.json').read_text(encoding='utf-8'))
    scope = {'_fabm_docs':lambda:docs}
    exec(compile(ast.Module(body=[node], type_ignores=[]),str(source),'exec'),scope)
    known = scope['_annotate_module']('POM','case authored original','有机质')
    assert known['desc'] == docs['modules']['POM']
    assert known['desc_en'] == docs['modules_en']['POM']
    assert known['category_en'] == 'Organic matter'
    custom = scope['_annotate_module']('Custom','Case original description','其他')
    assert custom['desc_en'] == 'Case original description'
