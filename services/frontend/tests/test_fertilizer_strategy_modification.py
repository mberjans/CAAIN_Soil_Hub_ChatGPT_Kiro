"""
Advanced fertilizer strategy modification interface tests.
"""

from pathlib import Path


def _load_template() -> str:
    """Read the fertilizer strategy template content for inspection."""
    template_path = Path(__file__).resolve().parents[1] / "src" / "templates" / "fertilizer_strategy.html"
    return template_path.read_text(encoding="utf-8")


def test_strategy_template_contains_modification_toolkit():
    """The template should include the advanced modification toolkit container and headings."""
    contents = _load_template()
    assert 'Interactive Strategy Builder' in contents
    assert 'id="modificationToolkit"' in contents
    assert 'Precision Adjusters' in contents


def test_strategy_template_references_real_time_scripts():
    """Verify required client-side libraries and functions exist in the template."""
    contents = _load_template()
    assert 'Sortable.min.js' in contents
    assert 'performRealTimeOptimization' in contents
    assert 'strategySteps' in contents
