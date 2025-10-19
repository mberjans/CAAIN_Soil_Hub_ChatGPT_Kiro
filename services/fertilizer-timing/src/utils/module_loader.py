"""
Utility helpers for loading modules from the fertilizer strategy service.

This module dynamically loads the existing fertilizer strategy codebase so the
fertilizer timing microservice can reuse domain logic without duplicating it.
"""

import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

logger = logging.getLogger(__name__)

# Resolve important directories
_UTILS_PATH = Path(__file__).resolve()
_SERVICES_DIR = _UTILS_PATH.parents[3]
_STRATEGY_DIR = _SERVICES_DIR / "fertilizer-strategy"
_STRATEGY_SRC_DIR = _STRATEGY_DIR / "src"


def _ensure_package(name: str, path: Path) -> ModuleType:
    """
    Ensure a package with the provided name exists in sys.modules.

    Args:
        name: Fully qualified package name.
        path: Filesystem path that should be part of the package search path.

    Returns:
        ModuleType representing the ensured package.
    """
    existing = sys.modules.get(name)
    if existing is not None:
        if not hasattr(existing, "__path__"):
            existing.__path__ = []
        if existing.__path__ is None:
            existing.__path__ = []
        path_str = str(path)
        if path_str not in existing.__path__:
            existing.__path__.append(path_str)
        return existing

    package = ModuleType(name)
    package.__path__ = [str(path)]
    sys.modules[name] = package
    return package


def _prepare_strategy_packages() -> None:
    """Register synthetic packages that mirror the fertilizer strategy layout."""
    if not _STRATEGY_SRC_DIR.exists():
        raise FileNotFoundError(
            f"Fertilizer strategy source directory not found at {_STRATEGY_SRC_DIR}"
        )

    try:
        import services as services_module  # pylint: disable=import-outside-toplevel
    except ImportError:
        services_module = ModuleType("services")
        services_module.__path__ = [str(_SERVICES_DIR)]
        sys.modules["services"] = services_module
    else:
        if not hasattr(services_module, "__path__"):
            services_module.__path__ = [str(_SERVICES_DIR)]
        else:
            path_str = str(_SERVICES_DIR)
            if path_str not in services_module.__path__:
                services_module.__path__.append(path_str)

    _ensure_package("services.fertilizer_strategy", _STRATEGY_DIR)
    _ensure_package("services.fertilizer_strategy.src", _STRATEGY_SRC_DIR)
    _ensure_package("services.fertilizer_strategy.src.models", _STRATEGY_SRC_DIR / "models")
    _ensure_package("services.fertilizer_strategy.src.services", _STRATEGY_SRC_DIR / "services")


def load_strategy_module(module_name: str, module_path: Path) -> ModuleType:
    """
    Load a module from the fertilizer strategy service.

    Args:
        module_name: Fully qualified name to register the module under.
        module_path: Path to the module file to load.

    Returns:
        The loaded module.
    """
    _prepare_strategy_packages()

    if module_name in sys.modules:
        return sys.modules[module_name]  # type: ignore[return-value]

    if not module_path.exists():
        raise FileNotFoundError(f"Strategy module not found at {module_path}")

    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load spec for module {module_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed loading module %s from %s: %s", module_name, module_path, exc)
        sys.modules.pop(module_name, None)
        raise

    return module


def get_strategy_src_dir() -> Path:
    """Expose the fertilizer strategy src directory for consumers."""
    return _STRATEGY_SRC_DIR


__all__ = ["load_strategy_module", "get_strategy_src_dir"]
