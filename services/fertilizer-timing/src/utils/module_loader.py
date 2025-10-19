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
from typing import Dict, Optional

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


def _ensure_services_namespace() -> ModuleType:
    """
    Ensure the root services namespace is available.

    Returns:
        ModuleType for the root services package.
    """
    try:
        services_module = sys.modules["services"]
    except KeyError:
        services_module = ModuleType("services")
        services_module.__path__ = [str(_SERVICES_DIR)]
        sys.modules["services"] = services_module
        return services_module

    if not hasattr(services_module, "__path__"):
        services_module.__path__ = []

    if services_module.__path__ is None:
        services_module.__path__ = []

    services_dir_str = str(_SERVICES_DIR)
    if services_dir_str not in services_module.__path__:
        services_module.__path__.append(services_dir_str)

    return services_module


def _prepare_strategy_packages() -> None:
    """Register synthetic packages that mirror the fertilizer strategy layout."""
    if not _STRATEGY_SRC_DIR.exists():
        raise FileNotFoundError(
            f"Fertilizer strategy source directory not found at {_STRATEGY_SRC_DIR}"
        )

    _ensure_services_namespace()

    _ensure_package("services.fertilizer_strategy", _STRATEGY_DIR)
    _ensure_package("services.fertilizer_strategy.src", _STRATEGY_SRC_DIR)
    _ensure_package("services.fertilizer_strategy.src.models", _STRATEGY_SRC_DIR / "models")
    _ensure_package("services.fertilizer_strategy.src.services", _STRATEGY_SRC_DIR / "services")


def ensure_service_packages(
    service_name: str,
    additional_packages: Optional[Dict[str, Path]] = None,
    filesystem_name: Optional[str] = None,
) -> Path:
    """
    Ensure dynamic import support for a named service.

    Args:
        service_name: Python package name to expose under the services namespace.
        additional_packages: Optional mapping of package suffix to filesystem path
            that should be registered beneath the service src namespace.
        filesystem_name: Optional directory name when it differs from the package name.

    Returns:
        Path to the service src directory.
    """
    _ensure_services_namespace()

    directory_name = filesystem_name or service_name
    service_dir = _SERVICES_DIR / directory_name
    if not service_dir.exists():
        raise FileNotFoundError(f"Service directory not found for {service_name}: {service_dir}")

    src_dir = service_dir / "src"
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found for {service_name}: {src_dir}")

    base_package = f"services.{service_name}"
    _ensure_package(base_package, service_dir)
    _ensure_package(f"{base_package}.src", src_dir)

    if additional_packages is not None:
        for package_suffix, package_path in additional_packages.items():
            package_name = f"{base_package}.src.{package_suffix}"
            _ensure_package(package_name, package_path)

    return src_dir


def get_services_root() -> Path:
    """Expose the root services directory for callers."""
    return _SERVICES_DIR


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


__all__ = [
    "ensure_service_packages",
    "get_services_root",
    "load_strategy_module",
    "get_strategy_src_dir",
]
