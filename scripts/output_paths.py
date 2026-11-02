"""Shared output-root policy for scripts that create generated artifacts."""
import os
from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path(r'D:\GETM-FABM-WET-outputs')


def require_outside_c(path, label='Output path'):
    """Resolve a path and reject writes whose resolved drive is C:."""
    resolved = Path(path).expanduser().resolve()
    if resolved.drive.upper() == 'C:':
        raise ValueError(f'{label} must be outside C:. Refusing to write to {resolved}')
    return resolved


def get_output_root():
    """Return the configured non-C output root, or the shared D: default."""
    configured = os.environ.get('WET_OUTPUT_ROOT')
    return require_outside_c(configured or DEFAULT_OUTPUT_ROOT, 'WET_OUTPUT_ROOT')


def output_path(*parts):
    """Join generated-output components below WET_OUTPUT_ROOT and validate."""
    return require_outside_c(get_output_root().joinpath(*parts))
