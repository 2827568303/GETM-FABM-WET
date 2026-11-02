"""Simulate only the explicit matplotlib exclusion, without building a release."""
import importlib.abc
import importlib.metadata
import json
import sys


class ExcludedMatplotlib(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'matplotlib' or fullname.startswith('matplotlib.'):
            raise ModuleNotFoundError('matplotlib excluded by build_app.py')


sys.meta_path.insert(0, ExcludedMatplotlib())
try:
    import pyabc
    result = {'import_succeeded': True}
except Exception as exc:
    result = {'import_succeeded': False, 'error_type': type(exc).__name__, 'error': str(exc)}
result.update(pyabc_version=importlib.metadata.version('pyabc'),
              scope='Import probe for explicit build exclusion; not a frozen executable test')
print(json.dumps(result, indent=2))
