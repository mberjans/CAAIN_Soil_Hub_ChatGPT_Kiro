"""Crop taxonomy service package root."""

from pathlib import Path as _Path
import sys as _sys

package_root = _Path(__file__).resolve().parent
if str(package_root) not in _sys.path:
    _sys.path.insert(0, str(package_root))

__all__ = []
